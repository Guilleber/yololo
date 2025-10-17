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
import multiprocessing
from multiprocessing import Process, Queue
from time import sleep
from typing import Any


def _process_source(source_name: Any, queue: multiprocessing.Queue) -> None:
    """Runs in a separate process to update one source."""
    from src.yololo.storage.ChromDB import ChromaDBStorage  # Import inside process
    from src.yololo.domain.source_directory import Source

    db = ChromaDBStorage()  # Reinitialize to get its own client safely
    source = Source[source_name]
    collection = db.client.get_collection(source.name)

    count = 0
    for docu in source.value().stream_newest():
        db.add_document(docu, collection)
        count += 1
        if count % 10 == 0:
            queue.put((source.name, count))

    queue.put((source.name, count))
    queue.put("DONE")

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
        """Parallel update of ChromaDB with periodic progress reporting."""

        print("🔄 Starting ChromaDB update...")

        # List collections (for initial count)
        total_docs = 0
        for collection_info in self.client.list_collections():
            collection_name = getattr(collection_info, "name", collection_info)
            collection = self.client.get_collection(collection_name)
            count = len(collection.get()["ids"])
            print(f"\t{collection_name}: {count} documents")
            total_docs += count
        print(f"\tTotal documents before update: {total_docs}")

        # Create a queue for progress messages
        progress_queue = Queue()

        # Spawn one process per Source
        processes = []
        for source in Source:
            p = Process(
                target=_process_source,
                args=(source.name, progress_queue),
            )
            p.start()
            processes.append(p)

        # Monitor progress
        finished = 0
        while finished < len(processes):
            try:
                msg = progress_queue.get(timeout=5)
                if msg == "DONE":
                    finished += 1
                else:
                    source_name, count = msg
                    print(f"✅ {source_name}: {count} new docs added")
            except Exception:
                # Timeout: no message recently, can print heartbeat if needed
                pass

        for p in processes:
            p.join()

        print("✅ All sources updated.")

        # Final summary
        total_docs = 0
        for collection_info in self.client.list_collections():
            collection_name = getattr(collection_info, "name", collection_info)
            collection = self.client.get_collection(collection_name)
            count = len(collection.get()["ids"])
            print(f"\t{collection_name}: {count} documents")
            total_docs += count
        print(f"\tTotal documents after update: {total_docs}")

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
