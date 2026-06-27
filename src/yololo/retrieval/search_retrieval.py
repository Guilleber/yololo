from tavily import TavilyClient

from yololo.retrieval.base import IRetrieval
from yololo.domain.document import Document


class TavilyRetrieval(IRetrieval):
    def __init__(self, api_key: str, max_results: int = 5):
        self._client = TavilyClient(api_key=api_key)
        self._max_results = max_results

    def query(self, text: str) -> list[Document]:
        response = self._client.search(
            query=text,
            search_depth="advanced",
            max_results=self._max_results,
            include_answer=False,
        )
        documents = []
        for result in response.get("results", []):
            documents.append(Document(
                title=result.get("title", ""),
                link=result.get("url", ""),
                content=result.get("content", ""),
            ))
        return documents
