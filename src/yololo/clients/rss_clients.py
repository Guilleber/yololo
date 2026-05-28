from yololo.clients.client import IClient
from yololo.domain.document import Document

from typing import Iterator


class BBCNewsClient(IClient):

    def __init__(self) -> None:
        self.name = "BBC News"
        self.base_url = "https://feeds.bbci.co.uk/news/world/rss.xml"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class NPRClient(IClient):

    def __init__(self) -> None:
        self.name = "NPR"
        self.base_url = "https://feeds.npr.org/1001/rss.xml"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class AlJazeeraClient(IClient):

    def __init__(self) -> None:
        self.name = "Al Jazeera"
        self.base_url = "https://www.aljazeera.com/xml/rss/all.xml"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class ProPublicaClient(IClient):

    def __init__(self) -> None:
        self.name = "ProPublica"
        self.base_url = "https://www.propublica.org/feeds/propublica/main"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class APNewsClient(IClient):
    # AP has no official RSS; Google News indexes AP articles reliably
    def __init__(self) -> None:
        self.name = "AP News"
        self.base_url = "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class APFactCheckClient(IClient):
    # AP has no official RSS; Google News indexes AP Fact Check reliably
    def __init__(self) -> None:
        self.name = "AP Fact Check"
        self.base_url = "https://news.google.com/rss/search?q=site:apnews.com+fact+check&hl=en-US&gl=US&ceid=US:en"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError


class ReutersClient(IClient):
    # Reuters killed their public RSS in 2020; Google News proxy is the reliable alternative
    def __init__(self) -> None:
        self.name = "Reuters"
        self.base_url = "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en"

    def stream_newest(self) -> Iterator[Document]:
        yield from self.retrieve_rss_flux(self.base_url)

    def retrieve_document(self, url: str) -> Document:
        raise NotImplementedError