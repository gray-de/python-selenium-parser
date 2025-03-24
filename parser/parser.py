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


options = webdriver.ChromeOptions() #создаем webdriver
options.page_load_strategy = "eager" #добавляем настройку в драйвер, чтобы не дожидаться полной подгрузки сайта(сайт долго грузиться, поэтому selenium простаивает)
options.add_argument("--ignore-certificate-errors --allow-insecure-localhost")
service = Service(executable_path=ChromeDriverManager().install()) # Service для инициализации, он устанавливает, создаёт и удаляет драйвер
driver = webdriver.Chrome(service=service, options=options) # Chrome будет управляться service'ом
driver.command_executor.set_timeout(1000)

root = ET.Element("articles")
k = 0
for num in range(1, 107): #перебираем все страницы с статьями
    driver.get(f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=medicine&view=default") #открываем одну страницу с статьями
    print(f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=medicine&view=default")
    time.sleep(3)
    links = driver.find_elements(By.CSS_SELECTOR, ".title-link") # находим объекты заголовков статей
    links_list = []
    for i in links:
        links_list.append(i.get_attribute("href")) # собираем в один список ссылке на статьи с этой страницы
    print(links_list)
    for i in links_list:
        try:
            driver.get(i) #открываем одну статью
            print(i)
            k += 1
        except ReadTimeoutError:
            driver.refresh()
        time.sleep(random.randint(3,6)) 
        try:
            element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".title.hypothesis_container"))) #добавляем ожидание в 10 секунд на появление на странице объекта, если он не успевает появится, то выводиться ошибка
        except TimeoutException:
            print("Time is out, skipping to the next text")
            break

        current_url = driver.current_url #переменная с ссылкой на страницу
        title = driver.find_element(By.CSS_SELECTOR, ".title.hypothesis_container").text #по css селектору находим заголовок статьи
        date = driver.find_element(By.CSS_SELECTOR, ".pubhistory").text #по css селектору находим даты статьи
        dates_list = date.split('/')
        res_dates_list = []
        while len(dates_list) < 4:
            dates_list.append('')
        for i in dates_list:
            res_dates_list.append(i[i.find(':')+2:])
        submission, revised, accepted, published = dates_list #разбиваем даты по переменным
        authors_list = driver.find_elements(By.CSS_SELECTOR, ".profile-card-drop") #по css селектору находим авторов
        authors = []
        for i in authors_list:
            authors.append(i.text) #добавляем авторов в отдельный список
        
        keywords = driver.find_elements(By.CSS_SELECTOR, ".html-gwd-group") #находим ключевые слова статьи
        keywords_list = []
        for i in keywords:
            keywords_list.append(i.text)
        if len(keywords_list) == 0:
            res_keywords = []
        else:
            str_keywords = keywords_list[0]
            res_keywords = str_keywords[9:].split(";")
        print(k)

        # Добавляем статью в XML
        article = ET.SubElement(root, "article")
        ET.SubElement(article, "title").text = title
        ET.SubElement(article, "url").text = current_url
        ET.SubElement(article, "submission_date").text = submission
        ET.SubElement(article, "revised_date").text = revised
        ET.SubElement(article, "accepted_date").text = accepted
        ET.SubElement(article, "published_date").text = published
        
        authors_elem = ET.SubElement(article, "authors")
        for author in authors:
            ET.SubElement(authors_elem, "author").text = author

        keywords_elem = ET.SubElement(article, "keywords")
        for keyword in res_keywords:
            ET.SubElement(keywords_elem, "keyword").text = keyword

# Записываем XML в файл
tree = ET.ElementTree(root)
with open("articles.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
