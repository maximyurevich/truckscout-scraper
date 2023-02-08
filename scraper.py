"""Scraper for truckscout24."""
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass
class Ad:
    id: int
    href: str
    title: str
    price: int
    mileage: int
    color: str
    power: int
    description: str


urls = []
page_count = 4

for i in range(0, page_count):
    urls.append(
        f"https://www.truckscout24.de"
        f"/transporter/gebraucht/kuehl-iso-frischdienst/renault"
        f"?currentpage={i}"
    )


def get_html(url: str):
    response = httpx.get(url).text
    return response


def get_ads_links():
    links = []

    for i in range(0, page_count):
        links.append(
            BeautifulSoup(get_html(urls[i]), "html.parser").select_one(
                ".ls-titles a"
            )["href"]
        )

    return links

def get_ad_data():
    pass


print(get_ads_links())
