# Importing Dependencies
import os
import logging
import asyncio
import pandas as pd

from src.process_query import process_query
from src.google_search_module import GoogleSearchModule
from src.url_filter import remove_redundant_links

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pipeline to process the query and return structured results
async def run_pipeline(query: str, column_name: str, df: pd.DataFrame):
    """
    Process the query and return structured results.
    """
    try:
        # Process the query
        search_queries = process_query(query, column_name, df)
        # Initialize Google Search Module
        search_module = GoogleSearchModule(search_queries)
        # Perform Google search
        url_results = await search_module.get_all_urls(search_queries)
        # Filter out redundant links
        filtered_results = remove_redundant_links(url_results)
        return filtered_results

    except Exception as e:
        logger.exception("An unexpected error occurred in the pipeline.")
        return None