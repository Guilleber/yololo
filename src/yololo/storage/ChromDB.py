from yololo.domain.document import Document
from yololo.clients.the_guardian_client import TheGuardianClient

import chromadb

class ChromaDBStorage:
    def __init__(self):
        # setup Chroma in-memory, for easy prototyping. Can add persistence easily!
        client = chromadb.Client()
        # Create collection. get_collection, get_or_create_collection, delete_collection also available!
        self.collection = client.create_collection("News_article")

    def add_document(self, document: Document):
        self.collection.add(
            documents=[document.content],
            # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
            metadatas=[{"title": document.title, "source": document.source}],  # filter on these!
            ids=[f"{document.title}_{document.source}"],  # unique for each doc
        )

    def add_rss(self, url:str) -> None:
        """
        Add all documents from a RSS Flux

        :param url:
        :return:
        """

        client= TheGuardianClient()
        for docu in client.retrieve_rss_flux(url):
            self.add_document(docu)

    def query(self, query: str) -> list[Document]:
        return self.collection.query(
            query_texts=[query],
            n_results=2
            )
