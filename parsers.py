# parsers.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import time
from selenium.common.exceptions import TimeoutException


def parse_reports_by_inn(inn):
    # Создаем экземпляр браузера
    driver = webdriver.Chrome()

    # URL сайта
    url = 'https://e-disclosure.ru/poisk-po-kompaniyam'

    # Открываем страницу
    driver.get(url)

    # Находим поле ввода и вводим ИНН
    input_field = driver.find_element(By.ID, 'textfield')
    input_field.send_keys(inn)
    search_button = driver.find_element(By.ID, 'sendButton')
    search_button.click()
    wait = WebDriverWait(driver, 10)
    cont_wrap_element = wait.until(EC.visibility_of_element_located((By.ID, 'cont_wrap')))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    company_link_element = soup.find('div', {'id': 'cont_wrap'}).find('a')
    relative_link = company_link_element['href']
    base_url = 'https://e-disclosure.ru'
    full_company_link = urljoin(base_url, relative_link)
    print(f"Название компании: {company_link_element.text.strip()}")
    driver.get(full_company_link)
    otchetnost_tab_element = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Отчетность')))
    otchetnost_tab_element.click()
    otchetnost_list_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[style="list-style-type: none;"]')))
    page_source_otchetnost = driver.page_source
    soup_otchetnost = BeautifulSoup(page_source_otchetnost, 'html.parser')
    otchetnost_block = soup_otchetnost.find('ul', {'style': 'list-style-type: none;'})
    otchetnost_items = otchetnost_block.find_all('li')
    otchetnost_names = []
    otchetnost_links = []
    for otchetnost_item in otchetnost_items:
        otchetnost_name = otchetnost_item.text.strip()
        otchetnost_relative_link = otchetnost_item.a['href']
        otchetnost_full_link = urljoin(base_url, otchetnost_relative_link)

        otchetnost_names.append(otchetnost_name)
        otchetnost_links.append(otchetnost_full_link)

    current_date_str = datetime.now().strftime("%d.%m.%Y")
    time.sleep(1)  # Даем время для прогрузки страницы с отчетностями
    matching_reports = []
    for name, link in zip(otchetnost_names, otchetnost_links):
        driver.get(link)
        try:
            table_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.zebra.noBorderTbl.centerHeader.files-table')))
        except TimeoutException:
            print(f"Таблица с информацией о документах не была найдена на странице {link}")
            continue

        # Получаем все строки таблицы
        rows = table_element.find_elements(By.TAG_NAME, 'tr')
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')

            # Извлекаем информацию
            if len(cells) >= 6:
                document_type = cells[1].text.strip()
                approval_date_cell = cells[4].text.strip()
                try:
                    approval_date = datetime.strptime(approval_date_cell, "%d.%m.%Y").strftime("%d.%m.%Y %H:%M")
                except ValueError:
                    approval_date = approval_date_cell

                # Проверяем, соответствует ли дата текущей дате
                if approval_date == current_date_str:
                    # Добавляем отчетность в список matching_reports
                    matching_reports.append({
                        "otchetnost_name": name,
                        "document_type": document_type,
                        "approval_date": approval_date,
                        "link": link
                    })

    time.sleep(1)
    driver.quit()

    # Возвращаем результат в виде словаря
    if matching_reports:
        reports_data = {
            "company_name": company_link_element.text.strip(),
            "reports": matching_reports
        }
        print(reports_data)
        return reports_data
    else:
        return {"company_name": company_link_element.text.strip(), "reports": []}