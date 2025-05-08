import chromadb
from chromadb.api.models import Collection

from yololo.domain.document import Document


class DocumentStorage:
    def __init__(self, collection: Collection | None = None):
        if collection is None:
            chroma_client = chromadb.Client()
            self.collection = chroma_client.create_collection(name="doc_storage")
        else:
            self.collection = collection

    def add_documents(self, documents: list[Document] | Document):
        if not isinstance(documents, list):
            documents = [documents]
        self.collection.add(
            documents=[doc.content for doc in documents],
            metadatas=[{"link": doc.link,
                        "title": doc.title,
                        "pub_date": doc.pub_date,
                        "language": doc.language,
                        "source": doc.source} for doc in documents],
            ids=[doc.title for doc in documents]  # TODO: find a better unique key
        )

    def query(self, query: str, result_size: int = 1) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            includes=["documents", "metadatas"],
            n_results=result_size
        )
        documents = []
        for document, metadata in zip(results.documents[0], results.metadata[0]):
            documents.append(Document(
                link=metadata["link"],
                title=metadata["title"],
                content=document,
                pub_date=metadata["pub_date"],
                language=metadata["language"],
                source=metadata["source"],
            ))
        return documents
