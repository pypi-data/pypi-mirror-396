"""Building engine to understand and process PDF files."""
# flake8: noqa: E402

import logging
import os

logger = logging.getLogger(__name__)

import asyncio
from collections import defaultdict

from ddtrace import tracer
from fastapi import HTTPException
from google.cloud.documentai_v1 import Document as docaiv1_document

from src.docai import _batch_process_pdf_w_docai, _process_pdf_w_docai
from src.excel_processing import extract_data_from_excel
from src.postprocessing.common import (
    format_all_entities,
    llm_prediction_to_tuples,
    remove_none_values,
)
from src.postprocessing.postprocess_booking_confirmation import (
    postprocess_booking_confirmation,
)
from src.postprocessing.postprocess_commercial_invoice import (
    postprocessing_commercial_invoice,
)
from src.postprocessing.postprocess_partner_invoice import (
    postprocessing_partner_invoice,
)
from src.prompts.prompt_library import prompt_library
from src.utils import (
    extract_top_pages,
    generate_schema_structure,
    get_pdf_page_count,
    get_processor_name,
    run_background_tasks,
    split_pdf_into_chunks,
    transform_schema_strings,
    validate_based_on_schema,
)


async def process_file_w_docai(
    params, image_content, client, processor_name, doc_type=None
):
    """
    Process a file using Document AI.

    Args:
        params (dict): The project parameters.
        image_content (bytes): The file to be processed. It can be bytes object.
        client: The Document AI client.
        processor_name (str): The name of the processor to be used.
        doc_type (str, optional): Document type for cost tracking labels.

    Returns:
        The processed document.

    Raises:
        ValueError: If the file is neither a path nor a bytes object.
    """
    result = None

    try:
        logger.info("Processing document...")
        result = await _process_pdf_w_docai(
            image_content, client, processor_name, doc_type=doc_type
        )
    except Exception as e:
        if e.reason == "PAGE_LIMIT_EXCEEDED":
            logger.warning(
                "Document contains more than 15 pages! Processing in batch method..."
            )
            # Process the document in batch method (offline processing)
            try:
                result = await _batch_process_pdf_w_docai(
                    params, image_content, client, processor_name, doc_type=doc_type
                )
            except Exception as batch_e:
                logger.error(f"Error processing document {batch_e}.")

        else:
            logger.error(f"Error processing document {e}.")

    return result


async def extract_data_from_pdf_w_docai(
    params,
    input_doc_type,
    file_content,
    processor_client,
    isBetaTest,
):
    """Extract data from the PDF file."""
    version = "stable" if not isBetaTest else "beta"
    processor_name = get_processor_name(params, input_doc_type, version)

    if not processor_name:
        supported_doc_types = list(params["data_extractor_processor_names"].keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document type {input_doc_type}. Supported document types are: {supported_doc_types}",  # noqa: E501
        )

    result = await process_file_w_docai(
        params, file_content, processor_client, processor_name, doc_type=input_doc_type
    )

    # Create an entity object to store the result in gcs
    result_for_store = docaiv1_document.to_json(result)

    aggregated_data = defaultdict(list)

    # Extract entities from the result
    for entity in result.entities:
        value = (
            {
                child.type_: (
                    child.mention_text,
                    child.page_anchor.page_refs[0].page
                    if hasattr(child.page_anchor.page_refs[0], "page")
                    else 0,
                )
                for child in entity.properties
            }
            if entity.properties
            else (
                entity.mention_text,
                entity.page_anchor.page_refs[0].page
                if hasattr(entity.page_anchor.page_refs[0], "page")
                else 0,
            )
        )
        aggregated_data[entity.type_].append(value)

    # Select only 1 entity for Occurrence_Type= "once"
    aggregated_data = await validate_based_on_schema(
        params, aggregated_data, processor_name
    )

    # Call postprocessing for Multi Leg
    if (
        input_doc_type == "bookingConfirmation"
        or input_doc_type == "bookingConfirmation_test"
    ):
        aggregated_data = postprocess_booking_confirmation(aggregated_data)
        logger.info("Transport Legs assembled successfully")
    elif input_doc_type in ["partnerInvoice", "customsInvoice"]:
        aggregated_data = postprocessing_partner_invoice(aggregated_data)
        logger.info("Partner Invoice naming changed successfully")

    response = await processor_client.get_processor(name=processor_name)
    processor_version = response.default_processor_version.split("/")[-1]

    logger.info("Data Extraction completed successfully")
    logger.info(
        f"Processor & it's version used for current request: {response.display_name} - {processor_version}"
    )

    return aggregated_data, result_for_store, processor_version


async def identify_carrier(
    document, llm_client, prompt, response_schema, doc_type=None
):
    """Identify the carrier from the Booking Confirmation document."""

    result = await llm_client.ask_gemini(
        prompt=prompt,
        document=document,
        response_schema=response_schema,
        response_mime_type="text/x.enum",
        doc_type=doc_type,
    )

    if result:
        result = result.strip().lower()
    else:
        result = "other"
    return result


async def process_file_w_llm(params, file_content, input_doc_type, llm_client):
    """Process a document using a language model (gemini) to extract structured data.

    Args:
        params (dict): The project parameters.
        file_content (str): The content of the file to be processed.
        input_doc_type (str): The type of document, used to select the appropriate prompt from the prompt library.
        llm_client: The LLM client object.

    Returns:
        result (dict): The structured data extracted from the document, formatted as JSON.
    """
    # Bundeskasse invoices contains all the required information in the first 3 pages.
    if input_doc_type == "bundeskasse":
        file_content = extract_top_pages(file_content, num_pages=5)

    number_of_pages = get_pdf_page_count(file_content)
    logger.info(f"processing {input_doc_type} with {number_of_pages} pages...")

    # get the schema placeholder from the Doc AI and generate the response structure
    response_schema = (
        prompt_library.library[input_doc_type]["other"]["placeholders"]
        if input_doc_type
        in [
            "partnerInvoice",
            "customsInvoice",
            "bundeskasse",
            "commercialInvoice",
            "packingList",
            "bookingConfirmation",
            "arrivalNotice",
            "finalMbL",
            "draftMbl",
        ]  # Move this to constants or remove after complete migration to LLM
        else generate_schema_structure(params, input_doc_type)
    )

    carrier = "other"
    carrier_schema = (
        prompt_library.library.get("preprocessing", {})
        .get("carrier", {})
        .get("placeholders", {})
        .get(input_doc_type)
    )

    if carrier_schema:
        carrier_prompt = prompt_library.library["preprocessing"]["carrier"]["prompt"]
        carrier_prompt = carrier_prompt.replace(
            "DOCUMENT_TYPE_PLACEHOLDER", input_doc_type
        )

        # convert file_content to required document
        document = llm_client.prepare_document_for_gemini(file_content)

        # identify carrier for customized prompting
        carrier = await identify_carrier(
            document,
            llm_client,
            carrier_prompt,
            carrier_schema,
            doc_type=input_doc_type,
        )

    # Select prompt
    if (
        input_doc_type not in prompt_library.library
        or carrier not in prompt_library.library[input_doc_type]
    ):
        return {}

    # get the related prompt from predefined prompt library
    prompt = prompt_library.library[input_doc_type][carrier]["prompt"]

    # Add page-number extraction for moderately large docs
    use_chunking = number_of_pages >= params["chunk_after"]

    # Update schema and prompt to extract value-page_number pairs
    if not use_chunking and number_of_pages > 1:
        response_schema = transform_schema_strings(response_schema)
        prompt += "\nFor each field, provide the page number where the information was found. The page numbering starts from 0."

    tasks = []
    # Process in chunks if number of pages exceeds threshold and Process all chunks concurrently
    for chunk in (
        split_pdf_into_chunks(file_content, chunk_size=params["chunk_size"])
        if use_chunking
        else [file_content]
    ):
        tasks.append(
            process_chunk_with_retry(
                chunk, prompt, response_schema, llm_client, input_doc_type
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    if use_chunking:
        return merge_llm_results(results, response_schema)
    else:
        return llm_prediction_to_tuples(results[0], number_of_pages=number_of_pages)


async def process_chunk_with_retry(
    chunk_content, prompt, response_schema, llm_client, input_doc_type, retries=2
):
    """Process a chunk with retries in case of failure."""
    for attempt in range(1, retries + 1):
        try:
            return await process_chunk(
                chunk_content=chunk_content,
                prompt=prompt,
                response_schema=response_schema,
                llm_client=llm_client,
                input_doc_type=input_doc_type,
            )
        except Exception as e:
            logger.error(f"Chunk failed on attempt {attempt}: {e}")
            if attempt == retries:
                raise
            await asyncio.sleep(1)  # small backoff


async def process_chunk(
    chunk_content, prompt, response_schema, llm_client, input_doc_type
):
    """Process a chunk with Gemini."""
    document = llm_client.prepare_document_for_gemini(chunk_content)
    return await llm_client.get_unified_json_genai(
        prompt=prompt,
        document=document,
        response_schema=response_schema,
        doc_type=input_doc_type,
    )


def merge_llm_results(results, response_schema):
    """Merge LLM results from multiple chunks."""
    merged = {}
    for i, result in enumerate(results):
        if not isinstance(result, dict):
            continue
        # Add page number to all values coming from this chunk
        result = llm_prediction_to_tuples(result, number_of_pages=1, page_number=i)

        # Merge the result into the final merged dictionary
        for key, value in result.items():
            field_type = (
                response_schema["properties"].get(key, {}).get("type", "").upper()
            )

            if key not in merged:
                if field_type == "ARRAY":
                    # append the values as a list
                    merged[key] = (
                        value if isinstance(value, list) else ([value] if value else [])
                    )
                else:
                    merged[key] = value
                continue

            if field_type == "ARRAY":
                # append list contents across chunks
                if isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key].append(value)

            # take first non-null value only
            if merged[key] in (None, "", [], {}):
                merged[key] = value

    return merged


async def extract_data_from_pdf_w_llm(params, input_doc_type, file_content, llm_client):
    """Extract data from the PDF file."""
    # Process the document using LLM
    result = await process_file_w_llm(params, file_content, input_doc_type, llm_client)

    # Add currency from the amount field
    if input_doc_type in ["commercialInvoice"]:
        result = postprocessing_commercial_invoice(result, params, input_doc_type)
    elif input_doc_type == "bookingConfirmation":
        result = postprocess_booking_confirmation(result)
    return result, llm_client.model_id


def combine_llm_results_w_doc_ai(
    doc_ai, llm, keys_to_combine: list = None, input_doc_type=None
):
    """
    Combine results from DocAI and LLM extractions.

    Args:
        doc_ai: result from DocAI
        llm: result from LLM
        keys_to_combine (list): specific keys to apply list merging logic (e.g., 'transportLegs' or 'containers')
        input_doc_type: document type

    Returns:
        combined result
    """
    result = doc_ai.copy()
    llm = remove_none_values(llm)
    if not llm:
        return result

    # Merge top-level keys
    result.update({k: v for k, v in llm.items() if k not in result})

    if (
        input_doc_type
        and input_doc_type in ["packingList", "commercialInvoice"]
        and keys_to_combine
    ):
        result.update(
            {key: llm.get(key) for key in keys_to_combine if key in llm.keys()}
        )
        return result

    # Handle specific key-based merging logic for multiple keys
    if keys_to_combine:
        for key in keys_to_combine:
            if key in llm.keys():
                # Merge the list of dictionaries
                # If the length of the LLM list is less than the Doc AI result, replace with the LLM list
                if len(llm[key]) < len(result[key]):
                    result[key] = llm[key]
                else:
                    # If the length of the LLM list is greater than or equal to the Doc AI result,
                    # add & merge the dictionaries
                    if isinstance(llm[key], list):
                        for i in range(len(llm[key])):
                            if i == len(result[key]):
                                result[key].append(llm[key][i])
                            else:
                                for sub_key in llm[key][i].keys():
                                    result[key][i][sub_key] = llm[key][i][sub_key]
    return result


async def extract_data_by_doctype(
    params,
    file_content,
    input_doc_type,
    processor_client,
    if_use_docai,
    if_use_llm,
    llm_client,
    isBetaTest=False,
):
    async def extract_w_docai():
        return await extract_data_from_pdf_w_docai(
            params=params,
            input_doc_type=input_doc_type,
            file_content=file_content,
            processor_client=processor_client,
            isBetaTest=isBetaTest,
        )

    async def extract_w_llm():
        return await extract_data_from_pdf_w_llm(
            params=params,
            input_doc_type=input_doc_type,
            file_content=file_content,
            llm_client=llm_client,
        )

    if if_use_docai and if_use_llm:
        results = await asyncio.gather(extract_w_docai(), extract_w_llm())
        (extracted_data_doc_ai, store_data, processor_version_doc_ai) = results[0]
        (extracted_data_llm, processor_version_llm) = results[1]

        # Combine the results from DocAI and LLM extractions
        logger.info("Combining the results from DocAI and LLM extractions...")
        extracted_data = combine_llm_results_w_doc_ai(
            extracted_data_doc_ai,
            extracted_data_llm,
            params["key_to_combine"][input_doc_type],
            input_doc_type,
        )
        processor_version = f"{processor_version_doc_ai}/{processor_version_llm}"
    elif if_use_docai:
        (extracted_data, store_data, processor_version) = await extract_w_docai()
    elif if_use_llm:
        (extracted_data, processor_version) = await extract_w_llm()
        store_data = extracted_data
    else:
        raise ValueError("Either if_use_docai or if_use_llm must be True.")
    return extracted_data, store_data, processor_version


async def data_extraction_manual_flow(
    params,
    file_content,
    mime_type,
    meta,
    processor_client,
    schema_client,
    use_default_logging=False,
):
    """
    Process a PDF file and extract data from it.

    Args:
        params (dict): Parameters for the data extraction process.
        file_content (bytes): The content of the PDF file to process.
        mime_type (str): The MIME type of the document.
        meta (DocumentMeta): Metadata associated with the document.
        processor_client (DocumentProcessorClient): Client for the Document AI processor.
        schema_client (DocumentSchemaClient): Client for the Document AI schema.

    Returns:
        dict: A dictionary containing the processed document information.

    Raises:
        Refer to reasons in 400 error response examples.
    """
    # Get the start time for processing
    start_time = asyncio.get_event_loop().time()

    # Select LLM client (Using 2.5 Pro model only for PI and customsInvoice)
    llm_client = (
        params["LlmClient_Flash"]
        if meta.documentTypeCode not in ["customsInvoice", "partnerInvoice"]
        else params["LlmClient"]
    )

    page_count = None
    # Validate the file type
    if mime_type == "application/pdf":
        # Enable Doc Ai only for certain document types.
        if_use_docai = (
            True if meta.documentTypeCode in params["model_config"]["stable"] else False
        )
        if_use_llm = (
            True if meta.documentTypeCode in params["key_to_combine"].keys() else False
        )

        (
            extracted_data,
            store_data,
            processor_version,
        ) = await extract_data_by_doctype(
            params,
            file_content,
            meta.documentTypeCode,
            processor_client,
            if_use_docai=if_use_docai,
            if_use_llm=if_use_llm,
            llm_client=llm_client,
            isBetaTest=False,
        )
        page_count = get_pdf_page_count(file_content)

    elif "excel" in mime_type or "spreadsheet" in mime_type:
        # Extract data from the Excel file
        extracted_data, store_data, processor_version = await extract_data_from_excel(
            params=params,
            input_doc_type=meta.documentTypeCode,
            file_content=file_content,
            mime_type=mime_type,
            llm_client=llm_client,
        )

        # Get sheet count from dd-trace span (set in extract_data_from_excel)
        # Note: we use the span metric instead of len(extracted_data) because
        # some sheets may fail extraction and not appear in extracted_data
        span = tracer.current_span()
        page_count = span.get_metric("est_page_count") if span else len(extracted_data)
        if page_count > 100:
            logger.warning(
                f"Check logic. Count of sheets in excel file is weirdly large: {page_count}"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF or Excel file.",
        )
    # Create the result dictionary with the extracted data
    extracted_data = await format_all_entities(
        extracted_data, meta.documentTypeCode, params, mime_type
    )
    result = {
        "id": meta.id,
        "documentTypeCode": meta.documentTypeCode,
        "data": extracted_data,
        "processor_version": processor_version,
    }

    # Log the time taken for processing
    end_time = asyncio.get_event_loop().time()
    elapsed_time = end_time - start_time
    logger.info(f"Time taken to process the document: {round(elapsed_time, 4)} seconds")

    # Schedule background tasks without using FastAPI's BackgroundTasks
    if (
        os.getenv("CLUSTER") != "ode"
    ) & use_default_logging:  # skip data export to bigquery in ODE environment
        asyncio.create_task(
            run_background_tasks(
                params,
                meta.id,
                meta.documentTypeCode,
                extracted_data,
                store_data,
                processor_version,
                mime_type,
                elapsed_time,
                page_count,
            )
        )
    return result
