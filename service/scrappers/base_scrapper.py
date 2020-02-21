import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError


class BaseScrapper:
    """A base class for user scrappers objects

        Attributes:
            specialization (str): attribute for describing the resource of scrapping,
            _source_url (str): url of source for scrapping.

        Methods:
            create_soup_obj: Creates BeautifulSoup object related to input url.

    """

    def __init__(self, url: str, specialization: str) -> None:
        self._source_url = url
        self.specialization = specialization

    @staticmethod
    def create_soup_obj(source_url: str) -> BeautifulSoup:
        """Creates BeautifulSoup object related to input url.

            Args:
                source_url (str): url of web page you want to scrap.

            Returns:
                BeautifulSoup: if source_url is correct, None otherwise.

            Raises:
                TypeError: if source_url is not a string.

        """
        if not isinstance(source_url, str):
            raise TypeError("URL should be string.")

        try:
            page_response = requests.get(source_url).text
            soup_obj = BeautifulSoup(page_response, features="html5lib")

            return soup_obj
        except ConnectionError:
            print(f"Failed to connect to {source_url}")
            # TODO: create retry logic

    def __repr__(self) -> str:
        return f"Scrapper for {self.specialization} source."
