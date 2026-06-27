import threading
from yololo.retrieval.base import IRetrieval
from yololo.storage.ChromDB import ChromaDBStorage
from yololo.domain.document import Document


class ChromaRetrieval(IRetrieval):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self._storage = ChromaDBStorage(persist_directory=persist_directory)
        thread = threading.Thread(target=self._storage.update_database, daemon=True)
        thread.start()

    def query(self, text: str) -> list[Document]:
        return self._storage.query(text)
