"""This module contains the postprocessing functions for the partner invoice."""
from rapidfuzz import fuzz, process

from src.io import logger
from src.utils import get_tms_mappings


def postprocessing_partner_invoice(partner_invoice):
    """Apply postprocessing to the partner invoice data."""
    # Flatten the invoice amount
    for amount in partner_invoice.get("invoiceAmount", {}):
        if isinstance(amount, list):
            amount = amount[0]
        if isinstance(amount, dict):
            partner_invoice.update(amount)
            break

    # Remove invoiceAmount - comes from DocAI
    if partner_invoice.get("invoiceAmount") is not None:
        partner_invoice.pop("invoiceAmount")

    # Remove containers - comes from DocAI
    # TODO: we can distribute containers to line items based on location proximity
    if partner_invoice.get("containers") is not None:
        partner_invoice.pop("containers")

    # Ensure only one item for optional multiple fields
    optional_multiple_list = [
        "dueDate",
        "eta",
        "etd",
        "fortoEntity",
        "hblNumber",
        "reverseChargeSentence",
    ]
    for k, v in partner_invoice.items():
        if (k in optional_multiple_list) and isinstance(v, list):
            partner_invoice[k] = v[0]

    # Update keys
    key_updates = {
        "pod": "portOfDischarge",
        "pol": "portOfLoading",
        "name": "lineItemDescription",
        "unit": "quantity",
    }

    def update_keys(d, key_updates):
        """
        Recursively updates keys in a dictionary according to a mapping provided in key_updates.

        d: The original dictionary
        key_updates: A dictionary mapping old key names to new key names

        return A new dictionary with updated key names
        """
        if isinstance(d, dict):
            return {
                key_updates.get(k, k): update_keys(v, key_updates) for k, v in d.items()
            }
        elif isinstance(d, list):
            return [update_keys(item, key_updates) for item in d]
        else:
            return d

    updated_data = update_keys(partner_invoice, key_updates)
    return updated_data


def post_process_bundeskasse(aggregated_data):
    """Post-process the Bundeskasse invoice data."""
    # Check if the Credit note number starts with ATS and classify it to Credit Note else Invoice
    invoice_type = (
        "bundeskasseCreditNote"
        if aggregated_data.get("creditNoteInvoiceNumber", {})
        .get("documentValue", "")
        .startswith("ATS")
        else "bundeskasseInvoice"
    )

    aggregated_data["documentType"] = {
        "documentValue": invoice_type,
        "formattedValue": invoice_type,
    }

    # Predefine mappings for tax codes
    tax_type_mappings = {
        "A0000": "Zölle (ohne EGKS-Zölle, Ausgleichs-, Antidumping- und Zusatzzölle, Zölle auf Agrarwaren) (ZOLLEU)",
        "B0000": "Einfuhrumsatzsteuer(EUSt)",
        "A3000": "Endgültige Antidumpingzölle(ANTIDUMPEU)",
    }

    line_items = aggregated_data.get("lineItem", [])
    is_recipient_forto = False  # Check if Forto account is in any line item

    # Process each line item
    for line_item in line_items:
        tax_type = line_item.get("taxType")
        if tax_type:
            # Map the tax type to the corresponding value
            line_item["name"]["formattedValue"] = tax_type_mappings.get(
                tax_type.get("documentValue"), line_item["name"]["documentValue"]
            )

        # Check if the deferredDutyPayer is forto
        deferredDutyPayer = line_item.get("deferredDutyPayer", {})
        lower = deferredDutyPayer.get("documentValue", "").lower()
        if any(key in lower for key in ["de789147263644738", "forto"]):
            is_recipient_forto = True

    update_recipient_and_vendor(aggregated_data, is_recipient_forto)


def update_recipient_and_vendor(aggregated_data, is_recipient_forto):
    """Update the recipient and vendor information in the aggregated data."""
    # Check if the "recipientName" and "recipientAddress" keys exist
    keys_to_init = ["recipientName", "recipientAddress", "vendorName", "vendorAddress"]
    for key in keys_to_init:
        aggregated_data.setdefault(key, {"formattedValue": "", "documentValue": ""})

    if is_recipient_forto:
        # Update the aggregated data with the recipient information
        aggregated_data["recipientName"][
            "formattedValue"
        ] = "Forto Logistics SE & Co KG"
        aggregated_data["recipientAddress"][
            "formattedValue"
        ] = "Schönhauser Allee 9, 10119 Berlin, Germany"

    # Update the vendor details always to Bundeskasse Trier
    aggregated_data["vendorName"]["formattedValue"] = "Bundeskasse Trier"
    aggregated_data["vendorAddress"][
        "formattedValue"
    ] = "Dasbachstraße 15, 54292 Trier, Germany"


async def process_partner_invoice(params, aggregated_data, document_type_code):
    """Process the partner invoice data."""
    # Post process bundeskasse invoices
    if document_type_code == "bundeskasse":
        post_process_bundeskasse(aggregated_data)
        return

    line_items = aggregated_data.get("lineItem", [])
    # Add debug logging
    logger.info(f"Processing partnerInvoice with {len(line_items)} line items")

    reverse_charge = None
    reverse_charge_info = aggregated_data.get("reverseChargeSentence")

    # Check if reverseChargeSentence exists and has the expected structure
    if isinstance(reverse_charge_info, dict):
        # Get the reverse charge sentence and Check if the reverse charge sentence is present
        rev_charge_sentence = reverse_charge_info.get("formattedValue", "")
        reverse_charge_value = if_reverse_charge_sentence(rev_charge_sentence, params)

        # Assign the reverse charge value to the aggregated data
        reverse_charge_info["formattedValue"] = reverse_charge_value
        reverse_charge = aggregated_data.pop("reverseChargeSentence", None)

    # Process everything in one go
    processed_items = await process_line_items_batch(params, line_items, reverse_charge)

    # Update your main data structure
    aggregated_data["lineItem"] = processed_items


async def process_line_items_batch(
    params: dict, line_items: list[dict], reverse_charge=None
):
    """
    Processes all line items efficiently using a "Split-Apply-Combine" strategy.
    """
    # To store items that need external API lookup
    pending_line_items = {}

    # Check Fuzzy Matching
    logger.info(f"Mapping line item codes with Fuzzy matching....")
    for i, item in enumerate(line_items):
        description_obj = item.get("lineItemDescription")

        if not description_obj or not description_obj.get("formattedValue"):
            continue
        # Get the formatted description text
        desc = description_obj["formattedValue"]

        # Find Fuzzy Match
        matched_code = find_matching_lineitem(
            desc,
            params["lookup_data"]["item_code"],
            params["fuzzy_threshold_item_code"],
        )

        if matched_code:
            # Set the code to the line item
            item["itemCode"] = {
                "documentValue": desc,
                "formattedValue": matched_code,
                "page": description_obj.get("page"),
            }
        else:
            # Store for batch API call
            pending_line_items[i] = desc

    # Batch API Call for Embedding lookups
    if pending_line_items:
        values_to_fetch = list(set(pending_line_items.values()))
        logger.info(f"Mapping {len(values_to_fetch)} line items from Embedding API...")

        # Await the batch response {"desc1": "code1", "desc2": "code2"}
        api_results = await get_tms_mappings(
            input_list=values_to_fetch, embedding_type="line_items"
        )

        # Merge API results back into original list
        for index, desc in pending_line_items.items():
            # Get result from API response, or None if API failed for that item
            forto_code = api_results.get(desc)

            # Update the original item
            line_items[index]["itemCode"] = {
                "documentValue": desc,
                "formattedValue": forto_code,  # Might be None if API failed
                "page": line_items[index]["lineItemDescription"].get("page"),
            }

    # Add reverse charge here if exists
    if reverse_charge:
        [
            item.update({"reverseChargeSentence": reverse_charge})
            for item in line_items
            if (
                (item.get("itemCode") and item["itemCode"]["formattedValue"] != "CDU")
                or not item.get("itemCode")
            )
        ]

    return line_items


def get_fuzzy_match_score(target: str, sentences: list, threshold: int):
    """Get the best fuzzy match for a target string from a list of candidates.

    Args:
        target (str): The string to match.
        sentences (list): List of strings to match against.
        threshold (int): Minimum score threshold to consider a match.

    Returns:
        tuple: (best_match, score) if above threshold, else (None, 0)
    """
    # Use multiprocessing to find the best match
    result = process.extractOne(
        target, sentences, scorer=fuzz.WRatio, score_cutoff=threshold
    )

    if result is None:
        return None, False

    match, score, index = result

    # return best_match if the best match score is above a threshold (e.g., 80)
    if match:
        return match, True

    return None, False


def if_reverse_charge_sentence(sentence: str, params):
    """Check if the reverse charge sentence is present in the line item."""
    reverse_charge_sentences = params["lookup_data"]["reverse_charge_sentences"]
    threshold = params["fuzzy_threshold_reverse_charge"]

    # Check if ("ARTICLE 144", "ART. 144") in the sentence
    if "ARTICLE 144" in sentence or "ART 144" in sentence:
        return False

    # Check if the sentence is similar to any of the reverse charge sentences
    _, is_reverse_charge = get_fuzzy_match_score(
        sentence, reverse_charge_sentences, threshold
    )

    return is_reverse_charge


def find_matching_lineitem(new_lineitem: str, kvp_dict: dict, threshold=90):
    """Find the best matching line item from the key-value pair dictionary using fuzzy matching.

    Args:
        new_lineitem (str): The new line item to be matched.
        kvp_dict (dict): The key-value pair dictionary with 'Processed Lineitem' as key and 'Forto SLI' as value.
        threshold (int): Minimum score threshold to consider a match.
    Returns:
        str: The best matching 'Forto SLI' value from the dictionary.
    """
    # Check if the new line item is already in the dictionary
    if new_lineitem in kvp_dict:
        return kvp_dict[new_lineitem]

    # Get the best fuzzy match score for the extracted line item
    match, _ = get_fuzzy_match_score(
        new_lineitem,
        list(kvp_dict.keys()),
        threshold,
    )

    if match:
        # find the code from the kvp_dict
        return kvp_dict[match]

    return None


async def associate_forto_item_code(line_item_data, params):
    """
    Associates Forto item codes to a list of line item descriptions.
    Args:
        line_item_data (dict): A dictionary where keys are original descriptions and values are cleaned descriptions.
        params (dict): Parameters containing lookup data and thresholds.

    Returns:
        list: A list of dictionaries with 'description' and 'itemCode' keys.
    """

    result = []
    pending_line_items = {}
    for desc, f_desc in line_item_data.items():
        # Get the Forto item code using fuzzy matching
        code = find_matching_lineitem(
            new_lineitem=f_desc,
            kvp_dict=params["lookup_data"]["item_code"],
            threshold=params["fuzzy_threshold_item_code"],
        )
        if code:
            result.append({"description": desc, "itemCode": code})
        else:
            pending_line_items[desc] = f_desc

    # Batch API Call for Embedding lookups
    if pending_line_items:
        api_results = await get_tms_mappings(
            input_list=list(pending_line_items.values()),
            embedding_type="line_items",
        )

        # Merge API results back into original list
        for desc, f_desc in pending_line_items.items():
            code = api_results.get(f_desc)
            result.append({"description": desc, "itemCode": code})

    return result
