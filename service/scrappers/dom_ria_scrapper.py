from service.scrappers.base_scrapper import BaseScrapper, BeautifulSoup
from bs4.element import Tag
from collections import namedtuple
import re

class DomRiaScrapper(BaseScrapper):
    """A class for scrapping domria resource
    """

    def __init__(self, url: str="https://dom.ria.com/uk/arenda-kvartir/lvov/?page=1",
                 name: str="DomRia listings") -> None:

        super().__init__(url, name)
        self.dom_ria_soup = BaseScrapper.create_soup_obj(url)
        self.catalog_class = "ticket-clear line"
        self.realty_inner_link_class = "realtyPhoto"
        self.location_info_class = "blue"
        self.house_price_class = "green size22"
        self.inner_meta_feature_class = "label grey"
        self.inner_meta_feature_value_class = "indent"

    def parse_meta(self, meta_keys, meta_values):

        meta_titles = [el.text.strip() for el in list(meta_keys)]
        meta_values = [el.text.strip() for el in list(meta_values)]

    def parse_url(self, url, base="https://dom.ria.com"):
        base_url = url.replace("/ru/", "/uk/")
        return base + base_url

    def parse_price(self, scrapped_price: str) -> int:
        scrapped_price = scrapped_price.replace(" ", "")
        price_end_index = scrapped_price.find("грн")

        scrapped_price = scrapped_price[:price_end_index]
        return int(scrapped_price)

    def parse_location(self, location: str) -> tuple:
        street_index = location.find("вул.")
        city_index = location.find("м.")

        city_district = (location[:street_index].split())[1]
        street = location[street_index: city_index].replace("вул. ", "").strip()

        Location = namedtuple("Location", ("district", "street"))
        city_location = Location(city_district, street)

        return city_location

    def scrap_single_listing(self, scrapped_data: Tag) -> dict:
        """Method for scrapping and creating structured data.

            Args:
                scrapped_data (Tag): html markup of single listing.

            Returns:
                dict: structured scrapped data from single listing.

            Raises:
                TypeError: if scrapped_data isn't a Tag object.

        """
        result = {}

        if not isinstance(scrapped_data, Tag):
            raise TypeError("type of scrapped_data should be Tag (row html markup)")

        img_src = scrapped_data.find("img")["src"]
        inner_link = scrapped_data.find("a", attrs={"class": re.compile(f"{self.realty_inner_link_class}.+$")})["href"]

        location = scrapped_data.find("a", attrs={"class": "blue"}).getText().strip()

        listing_location = self.parse_location(location)

        listing_price = self.parse_price(scrapped_data.find("b", attrs={"class": self.house_price_class}).getText())

        inner_content_soup = BaseScrapper.create_soup_obj(self.parse_url(inner_link))

        listing_feature = inner_content_soup.find_all("div", attrs={"class": self.inner_meta_feature_class})
        listing_feature_value = inner_content_soup.find_all("div", attrs={"class": self.inner_meta_feature_value_class})

        structured_meta = self.parse_meta(listing_feature, listing_feature_value)

        return result



    def __repr__(self):
        super().__repr__()
