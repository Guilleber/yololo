import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Union

import feedparser

from yololo.domain.document import Document


class IClient(ABC):
    @abstractmethod
    def retrieve_document(self, url: str) -> Union[Document, None]:
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
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                print(f"Title: {entry.title}")
                print(f"Link: {entry.link}")
                doc = Document(link=entry.link,
                               title=entry.title,
                               content=entry.summary,
                               pub_date=entry.published,
                               source="The Guardian")
                # TODO: Access other feed elements as needed
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return doc
