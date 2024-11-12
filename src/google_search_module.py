# Importing Dependencies
import re
import time
import asyncio
import aiohttp
import logging
from typing import List
from contextlib import contextmanager

from .google_search import search

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Google Search Module
class GoogleSearchModule:
    def __init__(self, queries: List[str]):
        self.queries = queries
        self.master_list = []
        self.successful_queries = 0

    async def get_url(self, query: str):
        retries = 0
        success = False
        filtered_urls = []

        while retries < 2 and not success:
            try:
                result = await asyncio.to_thread(search, query)

                url_list = [url for url in result]

                patterns = [
                    r'https?://(www\.)?twitter\.com/',
                    r'https?://(www\.)?youtube\.com/',
                    r'https?://(www\.)?linkedin\.com/',
                    r'https?://(www\.)?instagram\.com/',
                    r'https?://(www\.)?facebook\.com/'
                ]

                for url in url_list:
                    if not any(re.search(pattern, url) for pattern in patterns):
                        filtered_urls.append(url)

                success = True
                self.successful_queries += 1
                # Number of urls to be scraped for each query
                return list(filtered_urls)[:3]

            except Exception as e:
                retries += 1
                print(f"retry : {retries}")
                await asyncio.sleep(3)

        return filtered_urls

    async def get_all_urls(self, queries: List[str]):
        tasks = [self.get_url(query) for query in queries]
        urls = await asyncio.gather(*tasks)

        master_list = []
        successful_queries = 0

        for query, url_list in zip(queries, urls):
            if url_list:
                master_list.append({
                    'query': query,
                    'urls': url_list
                })
                successful_queries += 1

        logging.info(f"Scraped {sum(len(item['urls']) for item in master_list)} urls from {successful_queries}/{len(queries)} queries")

        return master_list
