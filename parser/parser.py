from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import xml.etree.ElementTree as ET
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import ReadTimeoutError
import time
import random
import re


options = webdriver.ChromeOptions()
options.page_load_strategy = "eager"
options.add_argument("--ignore-certificate-errors --allow-insecure-localhost")
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.command_executor.set_timeout(1000)


def add_empty_dates(text):
    dates = re.findall(r"(submission|revised|accepted|published).*?:\s*((?:\d{1,2}\s+[A-Za-z]+\s+\d{4})?)", text,
                       re.IGNORECASE)

    date_dict = {}
    for label, date_str in dates:
        date_dict[label.lower()] = date_str.strip() if date_str else ""

    return (
        date_dict.get("submission", ""),
        date_dict.get("revised", ""),
        date_dict.get("accepted", ""),
        date_dict.get("published", "")
    )


root = ET.Element("articles")
k = 0

with open("articles1.xml", "wb") as f:
    f.write(b'<?xml version="1.0" encoding="utf-8"?>\n<articles>\n')

    for num in range(1, 107):
        driver.get(
            f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=medicine&view=default")
        print(f"Processing page {num}")
        time.sleep(3)

        links = [i.get_attribute("href") for i in driver.find_elements(By.CSS_SELECTOR, ".title-link")]

        for link in links:
            try:
                driver.get(link)
                print(link)
                k += 1
            except ReadTimeoutError:
                driver.refresh()

            time.sleep(random.randint(3, 6))

            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".title.hypothesis_container"))
                )
            except TimeoutException:
                print("Timeout, skipping...")
                continue

            current_url = driver.current_url
            title = driver.find_element(By.CSS_SELECTOR, ".title.hypothesis_container").text
            date = driver.find_element(By.CSS_SELECTOR, ".pubhistory").text
            submission, revised, accepted, published = add_empty_dates(date)

            authors = [i.text for i in driver.find_elements(By.CSS_SELECTOR, ".profile-card-drop")]

            keywords = driver.find_elements(By.CSS_SELECTOR, ".html-gwd-group")
            keywords_list = keywords[0].text[10:].split("; ") if keywords else []

            # Запись XML непосредственно в файл
            f.write(f'  <article>\n'.encode())
            f.write(f'    <title>{title}</title>\n'.encode())
            f.write(f'    <url>{current_url}</url>\n'.encode())
            f.write(f'    <submission_date>{submission}</submission_date>\n'.encode())
            f.write(f'    <revised_date>{revised}</revised_date>\n'.encode())
            f.write(f'    <accepted_date>{accepted}</accepted_date>\n'.encode())
            f.write(f'    <published_date>{published}</published_date>\n'.encode())

            f.write(f'    <authors>\n'.encode())
            for author in authors:
                f.write(f'      <author>{author}</author>\n'.encode())
            f.write(f'    </authors>\n'.encode())

            f.write(f'    <keywords>\n'.encode())
            for keyword in keywords_list:
                f.write(f'      <keyword>{keyword}</keyword>\n'.encode())
            f.write(f'    </keywords>\n'.encode())

            f.write(f'  </article>\n'.encode())

    f.write(b'</articles>')

driver.quit()