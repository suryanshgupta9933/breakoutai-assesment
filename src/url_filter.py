# Importing Dependencies
import re
import tldextract
from urllib.parse import urlparse

from sklearn.metrics import jaccard_score
from sklearn.feature_extraction.text import CountVectorizer

# Function to extract domain name from URL
def domain_name_parser(url: str) -> str:
    extracted = tldextract.extract(url)
    domain = extracted.domain
    return str(domain)

# Function to preprocess the URL
def preprocess_url(url):
    try:
        last_part = url.rstrip('/').split('/')[-1]
        title = last_part.replace('-', ' ')
        title = re.sub(r'\d+', '', title)
        title = ' '.join(word.capitalize() for word in title.split()).lower()
        return title
    except Exception as e:
        return url

# Define the Jaccard similarity function
def jaccard_similarity(str1, str2):
    try:
        if not str1 or not str2:
            return 1
        vectorizer = CountVectorizer().fit_transform([str1, str2])
        vectors = vectorizer.toarray()
        return jaccard_score(vectors[0], vectors[1], average='weighted')
    except Exception as e:
        return 1

# Function to remove redundant links
def remove_redundant_links(links, similarity_threshold=0.3):
    result = []

    for item in links:
        query = item['query']
        urls = item['urls']
        unique_urls = []

        processed_links = [preprocess_url(url) for url in urls]
        domains_seen = set()

        for i, url in enumerate(urls):
            is_unique = True
            url_domain = domain_name_parser(url)

            # Check against previously added unique URLs
            for j in range(len(unique_urls)):
                similarity = jaccard_similarity(processed_links[i], preprocess_url(unique_urls[j]))
                unique_url_domain = domain_name_parser(unique_urls[j])

                if similarity > similarity_threshold or url_domain == unique_url_domain:
                    is_unique = False
                    # If similarity is 1 and domain is the same, pick the URL with shorter length
                    if similarity == 1 and len(url) > len(unique_urls[j]):
                        unique_urls[j] = url
                    break

            if is_unique:
                unique_urls.append(url)
                domains_seen.add(url_domain)

        result.append({'query': query, 'urls': unique_urls})
    
    return result