from abc import ABC, abstractmethod
from yololo.domain.document import Document


class IRetrieval(ABC):

    @abstractmethod
    def query(self, text: str) -> list[Document]:
        raise NotImplementedError
