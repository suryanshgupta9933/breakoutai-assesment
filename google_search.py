from bs4 import BeautifulSoup
import urllib.request
import random
from urllib.parse import urlparse, parse_qs, quote
import re
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# User agents to avoid blocking
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
]

# Proxy configuration
username = 'spxn1r0koz'
password = 'k3~3s5hqJboKnV3sVm'
proxy_url = f"http://{username}:{password}@in.smartproxy.com:10000"

proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

def filter_result(link):
    try:
        # Decode hidden URLs.
        if link.startswith('/url?'):
            o = urlparse(link, 'http')
            link = parse_qs(o.query)['url'][0]
        # Valid results are absolute URLs not pointing to a Google domain.
        o = urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link
    except Exception:
        pass

def fetch_google_search_urls(html):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Find all the anchor tags with href attributes
    links = soup.find_all('a', href=True)
    search_urls = []
    # Filter URLs, only keeping those that point to external sites and not other Google searches or services
    for link in links:
        filtered_url = filter_result(link['href'])
        if filtered_url is not None and not re.search(r'https?://\S+\.(jpg|jpeg|png|gif|bmp)', filtered_url):
            search_urls.append(filtered_url)
    return search_urls

def search(query: str):
    params = {
        'tld': 'com',  # Top-level domain, like 'com', 'co.uk', etc.
        'lang': 'en',  # Language, like 'en' for English, 'es' for Spanish, etc.
        'query': quote(query),  # The search query
        'tbs': '0',  # Time limits, 'qdr:h' for past hour, 'qdr:d' for past 24 hours, 'qdr:m' for past month
        'safe': 'off',  # Safe search, 'on' or 'off'
    }

    url_search = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&" \
        "btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&" % params

    user_agent = random.choice(user_agents)
    headers = {'User-Agent': user_agent,
               'Cache-Control': 'no-cache',
               'Pragma': 'no-cache'
            }
    req = urllib.request.Request(url_search, headers=headers)

    retries = 0
    max_retries = 2
    backoff_factor = 1

    while retries < max_retries:
        try:
            response = urllib.request.urlopen(req)
            html = response.read()
            time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
            urls = fetch_google_search_urls(html)
            return urls
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait = backoff_factor * (2 ** retries)
                logging.warning(f"HTTP 429 encountered. Retrying in {wait} seconds...")
                time.sleep(wait)
                retries += 1
            else:
                logging.error(f"HTTP error encountered: {e}")
                return []
        except Exception as e:
            logging.error(f"General error encountered: {e}")
            return []

    logging.error("Max retries exceeded.")
    return []