from yololo.domain.document import Document


class DocumentStorage:
    def __init__(self):
        raise NotImplementedError

    def add_document(self, document: Document):
        raise NotImplementedError

    def query(self, query: str) -> list[Document]:
        raise NotImplementedError
