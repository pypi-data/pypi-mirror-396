"""This module contains the functions to extract data from an Excel file."""
# flake8: noqa: E402
import logging

from ddtrace import tracer

logger = logging.getLogger(__name__)

import asyncio

import numpy as np
import pandas as pd

from src.llm import prompt_excel_extraction
from src.prompts.prompt_library import prompt_library
from src.utils import estimate_page_count, generate_schema_structure, get_excel_sheets


async def extract_data_from_sheet(
    llm_client, sheet_name, sheet, response_schema, doc_type=None
):
    logger.info(f"Processing sheet: {sheet_name}")
    excel_content = pd.DataFrame(sheet.values).dropna(how="all", axis=1)

    # Convert to Markdown format for the LLM model
    worksheet = (
        "This is from a excel. Pay attention to the cell position:\n"
        + excel_content.replace(np.nan, "").to_markdown(index=False, headers=[])
    )

    # Prompt for the LLM JSON
    prompt_docai = prompt_excel_extraction(worksheet)

    try:
        result = await llm_client.get_unified_json_genai(
            prompt_docai,
            response_schema=response_schema,
            doc_type=doc_type,
        )
    except Exception as e:
        result = {}
        logger.error(f"Error extracting data from LLM: {e}")

    return sheet_name, result


async def extract_data_from_excel(
    params,
    input_doc_type,
    file_content,
    mime_type,
    llm_client,
):
    """Extract data from the Excel file.

    Args:
        params (dict): Parameters for the data extraction process.
        input_doc_type (str): The type of the document.
        file_content (bytes): The content of the Excel file to process.
        mime_type (str): The MIME type of the file.
        llm_client: The LLM client to use for data extraction.

    Returns:
        formatted_data (list): A list of dictionaries containing the extracted data.
        result (list): The extracted data from the document.
        model_id (str): The ID of the model used for extraction.

    """
    # Generate the response structure
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
        ]
        else generate_schema_structure(params, input_doc_type)
    )

    # Load the Excel file and get ONLY the "visible" sheet names
    sheets, workbook = get_excel_sheets(file_content, mime_type)

    # Track the number of sheets in dd-trace
    span = tracer.current_span()
    if span:
        estimated_page_counts = [
            estimate_page_count(workbook[sheet]) for sheet in sheets
        ]
        est_page_count = sum(estimated_page_counts)
        span.set_metric("est_page_count", est_page_count)

    # Excel files may contain multiple sheets. Extract data from each sheet
    sheet_extract_tasks = [
        extract_data_from_sheet(
            llm_client,
            sheet_name,
            workbook[sheet_name],
            response_schema,
            doc_type=input_doc_type,
        )
        for sheet_name in sheets
    ]
    extracted_data = {k: v for k, v in await asyncio.gather(*sheet_extract_tasks)}

    return extracted_data, extracted_data, llm_client.model_id
