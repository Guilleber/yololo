from yololo.domain.document import Document
from yololo.domain.source_directory import Source
from yololo.domain.enums import Source_string
from yololo.clients.the_guardian_client import TheGuardianClient

from chromadb.config import Settings
from chromadb import PersistentClient
from chromadb.api.models import Collection
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
        #TODO : at some point, this should be a passable argument to have modulable choice of DB
        #TODO : I also don't like how this is organized, with the string and the clients being initialized from two different place
        # Could be better to have the string as a client parameter and call it from there, although I think it might lead to circular import
        #TODO : In that optic of modularity, sources should be initialized here and not in the enum
        for source in Source:
            self.client.get_or_create_collection(source.name)

    def _document_exists(self, doc_id: str) -> bool:
        try:
            result = self.collection.get(ids=[doc_id])
            return len(result["ids"]) > 0
        except Exception:
            return False

    def generate_id(document: Document) -> str:
        return hashlib.md5(f"{document.title}_{document.source}_{document.link}".encode()).hexdigest()

    def update_database(self) -> None:
        #TODO : Update is slow even with just RSS flux of the guardian. We should probably make it run on the background in async if we can't speed it up
        total_docs=0

        collection_names = self.client.list_collections()  # Returns list of collection names or collection objects
        total_docs = 0

        for collection_info in collection_names:
            # Depending on the Chroma version, list_collections() may return dicts or objects
            collection_name = collection_info.name if hasattr(collection_info, "name") else collection_info

            collection = self.client.get_collection(collection_name)
            items = collection.get()
            count = len(items["ids"])  # Number of documents in this collection
            print(f"\t{collection_name}: {count} documents")
            total_docs += count

        print(f"\tTotal documents in ChromaDB: {total_docs}")

        for source in Source:
            print(source.name, source.value)
            for docu in source.value.stream_newest():
                self.add_document(docu, self.client.get_collection(source.name))



        for collection_info in collection_names:
            # Depending on the Chroma version, list_collections() may return dicts or objects
            collection_name = collection_info.name if hasattr(collection_info, "name") else collection_info

            collection = self.client.get_collection(collection_name)
            items = collection.get()
            count = len(items["ids"])  # Number of documents in this collection
            print(f"\t{collection_name}: {count} documents")
            total_docs += count

    # for source in Source:
        #     #1 - Check oldest
        # fds

    def generate_id(self, document: Document) -> str:
        return hashlib.md5(f"{document.title}_{document.source}_{document.link}".encode()).hexdigest()

    def add_document(self, document: Document, collection: Collection) -> None:
        doc_id = self.generate_id(document)
        if not self._document_exists(doc_id):
            collection.add(
                documents=[document.content],
                metadatas=[{
                    "title": document.title,
                    "source": document.source,
                    "link": document.link
                }],
                ids=[doc_id]
            )

    def query(self, query: str) -> list[Document]:
        all_results = []

        for collection in self.client.list_collections():
            results = collection.query(
                query_texts=[query],
                n_results=2,
                include=["documents", "metadatas", "distances"]
            )

            for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
            ):
                all_results.append(
                    (dist, Document(
                        title=meta["title"],
                        source=meta["source"],
                        content=doc,
                        link=meta["link"]
                    ))
                )

        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x[0])

        # Return the top 2 documents
        return [doc for _, doc in all_results[:2]]
