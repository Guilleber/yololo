from typing import Union, Sequence

import chromadb
from chromadb.api.models import Collection

from yololo.domain.document import Document


class DocumentStorage:
    def __init__(self, collection: Union[Collection, None] = None):
        if collection is None:
            chroma_client = chromadb.Client()
            self.collection = chroma_client.create_collection(name="doc_storage")
        else:
            self.collection = collection

    def add_document(self, document: Document):
        self.collection.add(
            documents=[document.content],
            metadatas=[{"link": document.link,
                        "title": document.title,
                        "pub_date": document.pub_date,
                        "language": document.language,
                        "source": document.source}],
            ids=[f"{document.title}___{document.pub_date}"]
        )

    def add_documents(self, documents: Sequence[Document]):
        self.collection.add(
            documents=[doc.content for doc in documents],
            metadatas=[{"link": doc.link,
                        "title": doc.title,
                        "pub_date": doc.pub_date,
                        "language": doc.language,
                        "source": doc.source} for doc in documents],
            ids=[f"{doc.title}___{doc.pub_date}" for doc in documents]
        )

    def query(self, query: str, result_size: int = 1) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            n_results=result_size
        )
        return results
