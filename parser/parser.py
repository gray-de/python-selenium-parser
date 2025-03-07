from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Service для инициализации, он устанавливает, создаёт и удаляет драйвер
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument(" --disable-javascript") 
options.page_load_strategy = "eager"

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options) # Chrome будет управляться service'ом

k = 0
start_time = time.time()

for num in range(1, 501):
    driver.get(f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=engineering&view=default")
    print(f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=engineering&view=default")
    links = driver.find_elements(By.CSS_SELECTOR, ".title-link")
    links_list = []
    for i in links:
        links_list.append(i.get_attribute("href"))

    print(links_list)

    for i in links_list:
        driver.get(i)
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".title.hypothesis_container")))
        current_url = driver.current_url
        print(current_url)
        title = driver.find_element(By.CSS_SELECTOR, ".title.hypothesis_container").text
        date = driver.find_element(By.CSS_SELECTOR, ".pubhistory").text
        dates_list = date.split('/')
        res_dates_list = []
        while len(dates_list) < 4:
            dates_list.append('')
        for i in dates_list:
            res_dates_list.append(i[i.find(':')+2:])
        submission, revised, accepted, published = dates_list
        authors_list = driver.find_elements(By.CSS_SELECTOR, ".profile-card-drop")
        authors = []
        for i in authors_list:
            authors.append(i.text)
        
        keywords = driver.find_elements(By.CSS_SELECTOR, ".html-gwd-group")
        keywords_list = []
        for i in keywords:
            keywords_list.append(i.text)
        if len(keywords_list) == 0:
            res_keywords = []
        else:
            str_keywords = keywords_list[0]
            res_keywords = str_keywords[9:].split(";")
        k += 1
        print(title)
        print(res_dates_list)
        print(authors)
        
        print(res_keywords)
        print(k)
        print("\n")

end_time = time.time()
res_time = end_time - start_time
print(res_time)