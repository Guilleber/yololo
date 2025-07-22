from yololo.clients.client import IClient
from yololo.domain.document import Document

import requests, os

from typing import Iterator

class TheGuardianClient(IClient):

    def __init__(self) -> None:
        self.base_url = "https://content.guardianapis.com/search"
        self.name = "The Guardian"
        print("bitch")

    def stream_newest(self) -> Iterator[Document]:
        """
        Stream the newest documents in the Guardian stream, paginating through all results.

        :return: Iterator of Document objects
        """


        base_url = "https://content.guardianapis.com/search"
        page = 1
        page_size = 50  # Guardian API max page size

        while True:
            print('hellp')
            params = {
                "page": page,
                "page-size": page_size,
                "order-by": "newest",
                "show-fields": "bodyText",
                "api-key": os.getenv("GUARDIAN_API_KEY"),
            }

            res = requests.get(base_url, params=params)
            if res.status_code != 200:
                print(f"Request failed with status code {res.status_code}")
                print(res.text)
                break

            data = res.json()
            results = data["response"].get("results", [])

            if not results:
                break

            for dat in results:
                # Make sure required fields are present
                if "fields" in dat and "bodyText" in dat["fields"]:
                    yield Document(
                        link=dat["webUrl"],
                        title=dat["webTitle"],
                        content=dat["fields"]["bodyText"],
                        source="The Guardian"
                    )

            # Stop if we've reached the last page
            if page >= data["response"]["pages"]:
                break

            page += 1

    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        base_url = "https://content.guardianapis.com/search"

        params = {
            "page-size": 5,
            "order-by": "newest",
            "api-key": os.getenv("GUARDIAN_API_KEY"),  # Replace with your actual API key
        }

        res = requests.get(base_url, params=params)
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


if __name__ == "__main__":
    gg = TheGuardianClient()
    for doc in gg.stream_newest():
        print(doc)