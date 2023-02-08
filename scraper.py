"""Scraper for truckscout24."""
import asyncio
import re
from dataclasses import dataclass, asdict
from io import BytesIO
from typing import Optional
import json
import os

import httpx
from bs4 import BeautifulSoup
from PIL import Image

from playwright.sync_api import sync_playwright

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
    response = httpx.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def get_ads_links():
    links = []

    for i in range(page_count):
        links.append(
            BeautifulSoup(get_html(urls[i]), "lxml").select_one(".ls-titles a")["href"]
        )

    return links


def get_ads_data():
    ads = []
    url: str = "https://www.truckscout24.de"
    urls = [url + link for link in get_ads_links()]

    with sync_playwright() as p:
        for i in range(page_count):
            page_html = get_html(urls[i])
            soup = BeautifulSoup(page_html, "lxml")
            columns_soup = soup.select_one(".columns")

            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(urls[i])

            # For description

            browser.close()

            ads.append(
                dict(
                    id=i + 1,
                    href=urls[i],
                    title=soup.select_one(".sc-ellipsis").get_text(),
                    price=re.search(
                        r"€ (\d+\.?\d*)", soup.select_one(".d-price > h2").get_text()
                    ).group(1),
                    mileage=re.search(
                        r"(\d+\.?\d*) km", soup.select_one(".data-basic1").get_text()
                    ).group(1),
                    color=columns_soup.select_one("li:nth-child(n+9)")
                    .select_one("div:nth-child(n+2)")
                    .get_text(),
                    power=re.search(
                        r"(\d+\.?\d*) kW",
                        columns_soup.select_one("li:nth-child(n+11)")
                        .select_one("div:nth-child(n+2)")
                        .get_text(),
                    ).group(1),
                    description="",
                )
            )
    return ads


def main():
    if not os.path.exists("data"):
        os.mkdir("data")
    with open("data/data.json", "w") as data:
        data.write(json.dumps({}, indent=4))


if __name__ == "__main__":
    main()
