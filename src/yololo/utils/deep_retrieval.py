from typing import List

import chromadb
from chromadb import QueryResult
from chromadb.api.client import ClientAPI
from chromadb.api.models.Collection import Collection

from yololo.domain.document import Document


def chroma_collection(client: ClientAPI, documents: List[Document]) -> Collection:
    collection = client.create_collection("all_docs")
    collection.add(
        documents=[doc.content for doc in documents],
        # tokenization, embedding, and indexing automatically handled by chromadb
        metadatas=[{"source": doc.source} for doc in documents],
        ids=[f"doc{ind}" for ind, doc in enumerate(documents)],  # unique for each doc
    )
    return collection


def chroma_ir(query: str, documents_list: List[Document], n_ranked_results: int = 10) -> QueryResult:
    client = chromadb.Client()
    collection = chroma_collection(client, documents_list)
    results = collection.query(
        query_texts=[query],
        n_results=n_ranked_results,
        # where={"metadata_field": "is_equal_to_this"}, # optional filter
        # where_document={"$contains":"search_string"}  # optional filter
    )
    # TODO: find solution to query only retuning 1 result when requested multiple
    return results
