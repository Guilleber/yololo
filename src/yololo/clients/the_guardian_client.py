from tqdm import tqdm
from bs4 import BeautifulSoup

from yololo.clients.client import IClient
from yololo.domain.document import Document
from utils import request_content_no_interrupt


class TheGuardianClient(IClient):
    def retrieve_document(self, url: str) -> Document:
        """
        retrieve the document (e.g. article) found at the given url.

        :param url: the url of the document
        :return: the retrieved document
        """
        client = IClient() ##############################
        doc = None
        guardian_content = request_content_no_interrupt(url)
        link_contents = []
        if guardian_content is not None:
            # with open('./text.xml', 'w') as f:
            #     f.write(str(guardian_content))
            soup = BeautifulSoup(guardian_content, 'html5lib')
            for link in tqdm([f"https://www.theguardian.com{lnk.get('href')}" for lnk in soup.main.find_all('a') if
                              lnk.get('href')[0] == '/']):
                link_res = request_content_no_interrupt(link)
                if link_res is not None:
                    link_soup = BeautifulSoup(link_res, 'html5lib')
                    link_main = link_soup.main
                    if link_main is not None:
                        link_content = '\n'.join([cnt.text for cnt in link_main.find_all('p')])
                        link_contents.append((link, str(link_content)))
        return doc
