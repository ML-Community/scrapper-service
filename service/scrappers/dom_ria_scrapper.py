"""dom_ria_scrapper module for defining class for scrapping domria resource.

Imports:
BaseScrapper (class): base class for all scrappers,
bs4.Element.Tag/ResultSet (class): Elements for showing user a type of scrapped element,
collections.namedtuple (callable): for creating tuples with keys,
re (module): regular expressions for filtering scrapped data.

"""
from service.scrappers.base_scrapper import BaseScrapper, BeautifulSoup
from bs4.element import Tag, ResultSet
from collections import namedtuple
from functools import partialmethod
import re

from constants import MAXIMUM_AMOUNT_OF_PAGES_FOR_SCRAPPING, NEXT_PAGE


class DomRiaScrapper(BaseScrapper):
    """A class for scrapping domria resource

        Attributes:
            catalog_class (str): html class of domria catalog.
            realty_inner_link_class (str): html class of domria listing link.
            location_info_class (str): html class of domria location information.
            house_price_class (str): html class of domria price information.
            inner_meta_feature_class (str): html class of domria listing features.
            inner_meta_feature_value_class (str): html class of domria listing features values.

    """

    def __init__(self, url: str = "https://dom.ria.com/uk/arenda-kvartir/lvov/?page=1",
                 name: str = "DomRia listings") -> None:

        super().__init__(url, name)
        self.catalog_class = "ticket-clear line"
        self.realty_inner_link_class = "realtyPhoto"
        self.location_info_class = "blue"
        self.house_price_class = "green size22"
        self.inner_meta_feature_class = "label grey"
        self.inner_meta_feature_value_class = "indent"

    def parse_meta(self, meta_keys: ResultSet, meta_values: ResultSet) -> dict:
        """Method for parsing and returning structured meta information about listing.

            Args:
                meta_keys (ResultSet): listing features names.
                meta_values (ResultSet): listing features values.

            Returns:
                dict: structured kv-pairs of listing features.

            Raises:
                TypeError: rather meta_keys or meta_values are not iterable(ResultSet) objects.

        """
        meta_titles = [el.text.strip() for el in list(meta_keys)]
        meta_values = [el.text.strip() for el in list(meta_values)]

        structured_meta = dict(zip(meta_titles, meta_values))
        return structured_meta

    def parse_url(self, url: str, base: str = "https://dom.ria.com") -> str:
        """Method for parsing and returning correct url.

            Args:
                url (str): scrapped url,
                base (str): base of url.

            Returns:
                str: correct url for future scrapping.

            Raises:
                TypeError: if url or base is not a string.

        """
        base_url = url.replace("/ru/", "/uk/")
        return base + base_url

    def parse_price(self, scrapped_price: str) -> int:
        """Method for parsing and returning correct price.

            Args:
                scrapped_price (str): scrapped listing price.

            Returns:
                int: correct price.

            Raises:
                TypeError: if scrapped_price is not a string.

        """
        scrapped_price = scrapped_price.replace(" ", "")
        price_end_index = scrapped_price.find("грн")

        scrapped_price = scrapped_price[:price_end_index]
        return int(scrapped_price)

    def parse_location(self, location: str) -> tuple:
        """Method for parsing and returning correct listing location.

            Args:
                location (str): scrapped listing location.

            Returns:
                namedtuple: namedtuple object consist of listing district and street.

            Raises:
                TypeError: if location is not a string.

        """
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
                ValueError: if scrapping of some part of source gone wrong.

        """
        result = {}

        if not isinstance(scrapped_data, Tag):
            raise TypeError("type of scrapped_data should be Tag (row html markup)")

        img_src = scrapped_data.find("img").get("src") or scrapped_data.find("img").get("data-src")

        inner_link = scrapped_data.find("a", attrs={"class": re.compile(f"{self.realty_inner_link_class}.+$")})["href"]

        scrapped_location = scrapped_data.find("a", attrs={"class": self.location_info_class}).getText().strip()
        scrapped_price = scrapped_data.find("b", attrs={"class": self.house_price_class}).getText()

        inner_content_soup = BaseScrapper.create_soup_obj(self.parse_url(inner_link))
        scrapped_feature = inner_content_soup.find_all("div", attrs={"class": self.inner_meta_feature_class})
        scrapped_feature_value = inner_content_soup.find_all("div", attrs={"class": self.inner_meta_feature_value_class})

        listing_location = self.parse_location(scrapped_location)
        listing_price = self.parse_price(scrapped_price)

        structured_meta = self.parse_meta(scrapped_feature, scrapped_feature_value)

        result["price"] = listing_price
        result["img"] = img_src
        result["district"] = listing_location.district
        result["street"] = listing_location.street
        result.update(structured_meta)

        return result


    def paginate_page(self, current_page_url: str) -> str:
        """Method for changing current page of source to next.

            Args:
                current_page_url (str): current page of scrapping.

            Returns:
                str: url of next page for scrapping.

            Raises:
                TypeError: if current_page_url is not a string.

        """
        page_index = current_page_url.find("=") + NEXT_PAGE
        current_page_number = current_page_url[page_index:]

        return current_page_url.replace(current_page_number, str(int(current_page_number) + NEXT_PAGE))


    def general_scrapp(self) -> list:
        """Initial method for scrapping source.

            Returns:
                list: scrapped and well formatted listings.

        """
        resulted_listings = []
        domria_url = self._source_url

        try:
            page_soup = BaseScrapper.create_soup_obj(domria_url)
        except TypeError:
            print("Incorrect url for creating bs object.")
            # TODO: retry logic here...

        for _ in range(MAXIMUM_AMOUNT_OF_PAGES_FOR_SCRAPPING):
            catalog = page_soup.find_all("section", attrs={"class": re.compile(f"{self.catalog_class}.+$")})

            for listing in catalog:
                try:
                    listing_info = self.scrap_single_listing(listing)
                    resulted_listings.append(listing_info)
                except ValueError as err:
                    print(err)
                    continue
                except KeyError as err:
                    print("got wrong keys: ", err)

            domria_url = self.paginate_page(domria_url)
            page_soup = BaseScrapper.create_soup_obj(domria_url)

        print("No more pages left.")
        return resulted_listings

    def __repr__(self) -> str:
        super().__repr__()
