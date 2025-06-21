from abc import ABC, abstractmethod

from yololo.domain.document import Document
from yololo.utils import rss

from typing import Iterator


class IClient(ABC):
    @abstractmethod
    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        raise NotImplementedError


    def retrieve_rss_flux(self, url: str) -> Iterator[Document]:
        """
        Retrieves a whole rss flux from a given url and convert them to document

        :param url: the url of the rss flux
        :return: List of documents
        """
        docus = rss.read_feed(url)
        for i, docu in enumerate(docus):
            dd=Document(link=docu.link,
                        title=docu.title,
                        content=docu.content,
                        source="The Guardian")
            yield dd

