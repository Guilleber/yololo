from yololo.domain.document import Document
from yololo.clients.the_guardian_client import TheGuardianClient

from chromadb.config import Settings
from chromadb import PersistentClient
import chromadb

import os
import hashlib

class ChromaDBStorage:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize Chroma with persistence
        self.client = PersistentClient(path=self.persist_directory)

        # Use get_or_create_collection to avoid errors if it already exists
        self.collection = self.client.get_or_create_collection("News_article")

    def _document_exists(self, doc_id: str) -> bool:
        try:
            result = self.collection.get(ids=[doc_id])
            return len(result["ids"]) > 0
        except Exception:
            return False

    def generate_id(document: Document) -> str:
        return hashlib.md5(f"{document.title}_{document.source}_{document.link}".encode()).hexdigest()

    def add_document(self, document: Document):
        doc_id = generate_id(document)
        if not self._document_exists(doc_id):
            self.collection.add(
                documents=[document.content],
                metadatas=[{
                    "title": document.title,
                    "source": document.source,
                    "link": document.link
                }],
                ids=[doc_id]
            )

    def add_rss(self, url: str) -> None:
        client = TheGuardianClient()
        for docu in client.retrieve_rss_flux(url):
            self.add_document(docu)

    def query(self, query: str) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            n_results=2
        )
        # Reformat the results back into Document objects if needed
        return [
            Document(title=meta["title"], source=meta["source"], content=doc, link=meta["link"])
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]