from abc import ABC, abstractmethod

from yololo.domain.document import Document


class IClient(ABC):
    @abstractmethod
    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        raise NotImplementedError
