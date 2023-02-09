"""Scraper for truckscout24.de."""
import json
import os
import re
import time
from io import BytesIO
import uuid

import httpx
from bs4 import BeautifulSoup
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By

urls = []
page_count = 4

options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

for i in range(page_count):
    urls.append(
        f"https://www.truckscout24.de"
        f"/transporter/gebraucht/kuehl-iso-frischdienst/renault"
        f"?currentpage={i}"
    )


def get_html(url: str):
    """Get HTML from response.

    :param url: page url
    :type url: str
    """
    response = httpx.get(url).text
    return response


def download_image(url: str, image_name: int):
    """Download and save images.

    :param url: image url
    :type url: str
    """
    response = httpx.get(url)
    img = Image.open(BytesIO(response.content))
    img.save(f"{image_name}.jpg")


def get_ads_links():
    """Get ads links with bs4."""
    links = []

    for i in range(page_count):
        links.append(
            BeautifulSoup(get_html(urls[i]), "lxml").select_one(".ls-titles a")["href"]
        )

    return links


def get_ads_data():
    """Get ads data with selenium and bs4."""

    ads = []
    url: str = "https://www.truckscout24.de"
    urls = [url + link for link in get_ads_links()]

    for i in range(page_count):
        id = uuid.uuid4().hex
        os.mkdir(f"data/{id}")
        page_html = get_html(urls[i])

        soup = BeautifulSoup(page_html, "lxml")

        columns = soup.select_one(".columns")

        price = re.search(r"€ (\d+\.?\d*)", soup.select_one(".d-price > h2").get_text())

        mileage = re.search(
            r"(\d+\.?\d*) km", soup.select_one(".data-basic1").get_text()
        )

        color = re.search(
            r"Farbe\n(.+)\n",
            columns.get_text()
        )

        power = re.search(
            r"(\d+\.?\d*) kW",
            columns.get_text(),
        )

        carousel_items = soup.select(".as24-carousel__item")

        for j in range(3):
            download_image(
                carousel_items[j].select_one(".gallery-picture").img["data-src"],
                f"data/{id}/{j + 1}",
            )

        driver.get(urls[i])
        show_more = driver.find_element(By.CLASS_NAME, "show-more")

        if show_more.is_displayed():
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(5)

        description = (
            BeautifulSoup(driver.page_source, "lxml")
            .find("div", {"data-target": "[data-item-name='description']"})
            .get_text()
        )

        ads.append(
            dict(
                id=id,
                href=urls[i],
                title=soup.select_one(".sc-ellipsis").get_text(),
                price=0 if price is None else int(price.group(1).replace(".", "")),
                mileage=0
                if mileage is None
                else int(mileage.group(1).replace(".", "")),
                color="" if color is None
                else color.group(1),
                power=0 if power is None else int(power.group(1)),
                description=description,
            )
        )

    return ads


def main():
    """Main function."""
    if not os.path.exists("data"):
        os.mkdir("data")
    with open("data/data.json", "w") as data:
        data.write(json.dumps({"ads": get_ads_data()}, indent=4))


if __name__ == "__main__":
    main()
