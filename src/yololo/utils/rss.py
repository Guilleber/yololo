import email.utils
from time import mktime
from datetime import datetime

import feedparser

from yololo.domain.document import Document


def read_feed(url: str) -> list[Document]:
    data = feedparser.parse(url)
    documents = []
    for entry in data.entries:
        date = email.utils.parsedate(entry.published)
        documents.append(Document(
            link=entry.link,
            title=entry.title,
            pub_date=datetime.fromtimestamp(mktime(date)),
            content=entry.description
        ))
    return documents
