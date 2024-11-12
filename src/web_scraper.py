# Importing Dependencies
import os
import logging
import requests
import newspaper
from io import BytesIO
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to read PDF content
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
        return ""

# Function to read HTML content
def read_html_content(url):
    """
    Download and extract text from an HTML page using BeautifulSoup.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator="\n").strip()
        
        logger.info(f"Scraped the article from: {url}")
        return text
    except Exception as e:
        logger.error(f"Failed to read HTML content at {url}: {e}")
        return ""

# Function to scrape webpages and handle binary files
def scraper(filtered_data):
    """
    Scrape web pages and download binary files if necessary.
    """
    try:
        for data in filtered_data:
            urls = data['urls']
            context = ""
            # Scrape each URL
            for url in urls:
                # Check if the URL is a PDF file
                if url.endswith('.pdf'):
                    # Process pdf content
                    pdf_content = read_pdf_content(url)
                    if pdf_content:
                        context += pdf_content
                    else:
                        logger.warning(f"Could not extract content from binary file: {url}")
                    continue

                # Check if the URL is an HTML page
                if url.endswith('.html') or url.endswith('.htm'):
                    # Process html content
                    html_content = read_html_content(url)
                    if html_content:
                        context += html_content
                    else:
                        logger.warning(f"Could not extract content from HTML file: {url}")
                    continue

                # Process web content
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

    except Exception as e:
        logger.error(f"Error in web scraping: {e}")
        # Append empty context on error for the failed query
        data['scraped_text'] = ""

    return filtered_data