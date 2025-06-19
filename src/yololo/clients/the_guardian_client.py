from yololo.clients.client import IClient
from yololo.domain.document import Document

import requests, os

from typing import Iterator

class TheGuardianClient(IClient):

    def __init__(self) -> None:
        self.base_url = "https://content.guardianapis.com/search"
        self.name = "The Guardian"


    def stream_newest(self) -> Iterator[dict]:
        """
        Stream the newest documents in theGuardian stream

        :return:
        """

        # TODO: Figure out how to get all newest eventually
        base_url = "https://content.guardianapis.com/search"

        params = {
            "page-size": 5,
            "order-by": "newest",
            "api-key": os.getenv("GUARDIAN_API_KEY"),  # Replace with your actual API key
        }

        res = requests.get(base_url, params=params)

        # Check if the request was successful
        if res.status_code == 200:
            data = res.json()
            print(data["results"])
        else:
            print(f"Request failed with status code {res.status_code}")
            print(res.text)

    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        raise NotImplementedError


class TheGuardianRSSClient(IClient):

    def __init__(self) -> None:
        self.name = "The Guardian RSS"
        self.base_url = "https://www.theguardian.com/international/rss"

    def stream_newest(self) -> Iterator[dict]:
        client = TheGuardianClient()
        for docu in client.retrieve_rss_flux(self.base_url):
            yield docu

    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        raise NotImplementedError


