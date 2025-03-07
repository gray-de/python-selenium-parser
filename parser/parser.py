from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions() #создаем webdriver
options.page_load_strategy = "eager" #добавляем настройку в драйвер, чтобы не дожидаться полной подгрузки сайта(сайт долго грузиться, поэтому selenium простаивает)

service = Service(executable_path=ChromeDriverManager().install()) # Service для инициализации, он устанавливает, создаёт и удаляет драйвер
driver = webdriver.Chrome(service=service, options=options) # Chrome будет управляться service'ом

for num in range(1, 501): #перебираем все страницы с статьями
    driver.get(f"https://www.mdpi.com/search?sort=pubdate&page_no={num}&page_count=50&year_from=1996&year_to=2025&q=engineering&view=default") #открываем одну страницу с статьями
    links = driver.find_elements(By.CSS_SELECTOR, ".title-link") # находим объекты заголовков статей
    links_list = []
    for i in links:
        links_list.append(i.get_attribute("href")) # собираем в один список ссылке на статьи с этой страницы

    for i in links_list:
        driver.get(i) #открываем одну статью
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".title.hypothesis_container"))) #добавляем ожидание в 5 секунд на появление на странице объекта, если он не успевает появится, то выводиться ошибка
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
    
        print(title)
        print(res_dates_list)
        print(authors)
        print(current_url)
        print(res_keywords)
        print("\n")
