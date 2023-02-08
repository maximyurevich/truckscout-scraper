"""Scraper for truckscout24."""
import json
import os
import re
import time
from io import BytesIO

import httpx
from bs4 import BeautifulSoup
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By

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


options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


def get_ads_data():
    ads = []
    url: str = "https://www.truckscout24.de"
    urls = [url + link for link in get_ads_links()]

    for i in range(page_count):
        page_html = get_html(urls[i])
        soup = BeautifulSoup(page_html, "lxml")
        columns_soup = soup.select_one(".columns")
        driver.get(urls[i])

        show_more = driver.find_element(By.CLASS_NAME, "show-more")

        if show_more.is_displayed():
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(5)

        print(driver.page_source)
        ads.append(
            dict(
                id=i + 1,
                href=urls[i],
                title=soup.select_one(".sc-ellipsis").get_text(),
                price=int(
                    re.search(
                        r"€ (\d+\.?\d*)", soup.select_one(".d-price > h2").get_text()
                    )
                    .group(1)
                    .replace(".", "")
                ),
                mileage=int(
                    re.search(
                        r"(\d+\.?\d*) km", soup.select_one(".data-basic1").get_text()
                    )
                    .group(1)
                    .replace(".", "")
                ),
                color=columns_soup.select_one("li:nth-child(n+9)")
                .select_one("div:nth-child(n+2)")
                .get_text(),
                power=int(
                    re.search(
                        r"(\d+\.?\d*) kW",
                        columns_soup.select_one("li:nth-child(n+11)")
                        .select_one("div:nth-child(n+2)")
                        .get_text(),
                    ).group(1)
                ),
                description=BeautifulSoup(driver.page_source, "lxml")
                .select_one(".short-description")
                .prettify(),
            )
        )
    return ads


def main():
    if not os.path.exists("data"):
        os.mkdir("data")
    with open("data/data.json", "w") as data:
        data.write(json.dumps({"ads": get_ads_data()}, indent=4))


if __name__ == "__main__":
    main()
