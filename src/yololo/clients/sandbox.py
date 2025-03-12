import requests
from typing import Union

import feedparser


def retrieve_document(url: str):
    """
    retrieve the document (e.g. article) found at the given url.
    Documentation source: https://feedparser.readthedocs.io/en/latest/

    :param url: the url of the document
    :return: the retrieved document
    """
    doc = None
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        with open('./text.xml', 'w') as f:
            f.write(str(response.content))
        feed = feedparser.parse(response.content)
        
        for entry in feed.feed.links:
            print(10000000000000, type(entry), entry.keys(), entry.type)
            
            print(f"Title: {entry.title}")
            print(f"Link: {entry.link}")
            # doc = Document(link=entry.link,
            #                title=entry.title,
            #                content=entry.summary,
            #                pub_date=entry.published,
            #                source="The Guardian")
            # TODO: Access other feed elements as needed
    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return doc


print(retrieve_document('https://theguardian.com'))
