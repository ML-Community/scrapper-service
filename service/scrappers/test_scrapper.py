from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import json


def parse_url(url, base="https://dom.ria.com"):
    base_url = url.replace("/ru/", "/uk/")
    return base + base_url


def parse_location(location: str) -> tuple:
    # р‑н. Франківський вул. Повстанська  м. Львів
    street_index = location.find("вул.")
    city_index = location.find("м.")

    city_district = (location[:street_index].split())[1]

    street = location[street_index: city_index].replace("вул. ", "").strip()

    return city_district, street


work_html = requests.get("https://dom.ria.com/uk/arenda-kvartir/lvov/?page=1").text

soup = BeautifulSoup(work_html, features="html5lib")

catalog = soup.find_all("section", attrs={"class": re.compile("ticket-clear line.+$")})[0]

#print(catalog)


img = catalog.find("img")["src"]

print(f"Img src: {img}")

url_more_info = catalog.find("a", attrs={"class": re.compile("realtyPhoto.+$")})["href"]

print(f"Url for more info: {parse_url(url_more_info)}")

location_info = catalog.find("a", attrs={"class": "blue"}).getText().strip()

print(location_info)
print(f"City district: {parse_location(location_info)}")

house_price = catalog.find("b", attrs={"class": "green size22"}).getText()

print(f"House price: {house_price}")

# short_descr = catalog.find("ul", attrs={"class": re.compile("mb-10.+$")}).find_all("li")
#
# print([el.text for el in list(short_descr)])

inner_content = requests.get(parse_url(url_more_info))

inner_content_soup = BeautifulSoup(inner_content.text, features="html5lib")

print()
#
# print(inner_content_soup.find("div", attrs={"id": "description"}))

some_meta = inner_content_soup.find_all("div", attrs={"class": "label grey"})
value_meta = inner_content_soup.find_all("div", attrs={"class": "indent"})

meta_titles = [el.text.strip() for el in list(some_meta)]
meta_values = [el.text.strip() for el in list(value_meta)]


print(list(zip(meta_titles, meta_values)))
