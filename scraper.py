"""Scraper for truckscout24."""
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from typing import Optional
from io import BytesIO
from PIL import Image
import re


@dataclass
class Ad:
    id: int
    href: str
    title: str
    price: int | str
    mileage: Optional[int | str]
    color: Optional[str]
    power: Optional[int]
    description: str


urls = []
page_count = 4

for i in range(page_count):
    urls.append(
        f"https://www.truckscout24.de"
        f"/transporter/gebraucht/kuehl-iso-frischdienst/renault"
        f"?currentpage={i}"
    )


def get_html(url: str):
    response = httpx.get(url).text
    return response


def download_image(url: str):
    pass


def get_ads_links():
    links = []

    for i in range(page_count):
        links.append(
            BeautifulSoup(get_html(urls[i]), "html.parser").select_one(".ls-titles a")[
                "href"
            ]
        )

    return links


def get_ads_data():
    ads = []
    url: str = "https://www.truckscout24.de"
    urls = [url + link for link in get_ads_links()]

    for i in range(page_count):
        page_html = get_html(urls[i])
        soup = BeautifulSoup(page_html, "html.parser")

        ads.append(
            Ad(
                id=i + 1,
                href=urls[i],
                title=soup.select_one(".sc-ellipsis").get_text(),
                price=soup.select_one(".d-price > h2").get_text(),
                mileage="",
                color="",
                power=0,
                description="",
            )
        )
    return ads


print(get_ads_data())
