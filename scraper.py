"""Scraper for truckscout24."""
import asyncio
import re
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import httpx
import pyppeteer
from bs4 import BeautifulSoup
from PIL import Image


@dataclass
class Ad:
    id: int
    href: str
    title: str
    price: int | str
    mileage: int
    color: Optional[str]
    power: Optional[int | str]
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

        columns_soup = soup.select_one(".columns")

        ads.append(
            Ad(
                id=i + 1,
                href=urls[i],
                title=soup.select_one(".sc-ellipsis").get_text(),
                price=soup.select_one(".d-price > h2").get_text(),
                mileage=int(
                    re.search(r"(\d+\.?\d*) km", 
                    soup.select_one(".data-basic1")\
                        .get_text()
                    )
                    .group(1)
                ),
                color=columns_soup.select_one("li:nth-child(n+9)")
                .select_one("div:nth-child(n+2)")
                .get_text(),
                power=columns_soup.select_one("li:nth-child(n+11)")
                .select_one("div:nth-child(n+2)")
                .get_text(),
                description="",
            )
        )
    return ads


print(get_ads_data())
