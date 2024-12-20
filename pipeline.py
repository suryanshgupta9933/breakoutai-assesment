# Importing Dependencies
import os
import logging
import asyncio
import pandas as pd

from src.search_query import preprocess
from src.google_search_module import GoogleSearchModule
from src.url_filter import remove_redundant_links
from src.web_scraper import scraper
from src.retriever import retrieve_context
from src.llm_query import generate_field_name, generate_field_data

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
        search_queries = preprocess(query, column_name, df)
        # Initialize Google Search Module
        search_module = GoogleSearchModule(search_queries)
        # Perform Google search
        url_results = await search_module.get_all_urls(search_queries)
        # Filter out redundant links
        filtered_results = remove_redundant_links(url_results)
        # Scrape the urls to extract text
        scraped_data = scraper(filtered_results)
        # Retrieve relevant context
        retrieved_data = await retrieve_context(scraped_data)
        # Generate field name
        field_name = generate_field_name(query)
        # Generate field data
        field_data = await generate_field_data(field_name, retrieved_data)
        # Append field name and data to df
        df[field_name] = field_data
        logger.info(f"Successfully processed query: {query}")
        return df

    except Exception as e:
        logger.exception("An unexpected error occurred in the pipeline.")
        return None