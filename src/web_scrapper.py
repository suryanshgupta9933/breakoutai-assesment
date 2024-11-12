# Importing Dependencies
import os
import logging
import requests
import newspaper
from io import BytesIO
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_binary_file(url):
    """
    Determine if the file is binary based on file extension.
    """
    return url.endswith(('.pdf'))

def read_pdf_content(url):
    """
    Download and extract text from a PDF file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        
        # Load PDF content with PyPDF2
        pdf_reader = PdfReader(BytesIO(response.content))
        pdf_text = ""
        for page_num in range(len(pdf_reader.pages)):
            pdf_text += pdf_reader.pages[page_num].extract_text() + "\n\n"
        
        logger.info(f"Scrapped the pdf from: {url}")
        return pdf_text
    except Exception as e:
        logger.error(f"Failed to read pdf at {url}: {e}")
        return None

# Function to scrape webpages and handle binary files
def scrapper(filtered_data):
    """
    Scrape web pages and download binary files if necessary.
    """
    try:
        for data in filtered_data:
            urls = data['urls']
            context = ""
            # Scrape each URL
            for url in urls:
                if is_binary_file(url):
                    # Process binary files (e.g., PDFs)
                    pdf_content = read_pdf_content(url)
                    if pdf_content:
                        context += pdf_content
                    else:
                        logger.warning(f"Could not extract content from binary file: {url}")
                    continue

                # Process HTML content
                try:
                    article = newspaper.Article(url, language="en")
                    article.download()
                    article.parse()
                    logger.info(f"Scraped the article from: {url}")
                    context += article.text + "\n\n"
                except Exception as parse_error:
                    logger.error(f"Failed to parse article at {url}: {parse_error}")
                    continue

            # Store the scraped content in the data dictionary
            data['scraped_text'] = context
        return filtered_data

    except Exception as e:
        logger.error(f"Error in web scraping: {e}")
        return None