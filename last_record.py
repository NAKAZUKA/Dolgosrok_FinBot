# last_record.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import time
from selenium.common.exceptions import TimeoutException

def parse_last_report_by_inn(inn):
    # Создаем экземпляр браузера
    driver = webdriver.Chrome()

    # URL сайта
    url = 'https://e-disclosure.ru/poisk-po-kompaniyam'

    # Открываем страницу
    driver.get(url)

    # Находим поле ввода и вводим ИНН
    input_field = driver.find_element(By.ID, 'textfield')
    input_field.send_keys(inn)

    # Находим кнопку "Искать" и кликаем по ней
    search_button = driver.find_element(By.ID, 'sendButton')
    search_button.click()

    # Ждем, пока элемент с id 'cont_wrap' станет видимым (ждем не более 10 секунд)
    wait = WebDriverWait(driver, 10)
    cont_wrap_element = wait.until(EC.visibility_of_element_located((By.ID, 'cont_wrap')))

    # После успешного ожидания, продолжаем парсить страницу
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Находим ссылку на компанию в таблице результатов
    company_link_element = soup.find('div', {'id': 'cont_wrap'}).find('a')
    relative_link = company_link_element['href']

    # Формируем полный URL
    base_url = 'https://e-disclosure.ru'
    full_company_link = urljoin(base_url, relative_link)

    # Выводим найденные данные
    print(f"Название компании: {company_link_element.text.strip()}")

    # Переходим по полной ссылке
    driver.get(full_company_link)

    # Ждем, пока появится вкладка "Отчетность" (ждем не более 10 секунд)
    otchetnost_tab_element = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Отчетность')))
    otchetnost_tab_element.click()

    # Ждем, пока появится список отчетности
    otchetnost_list_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[style="list-style-type: none;"]')))

    # После успешного ожидания, продолжаем парсить страницу "Отчетность"
    page_source_otchetnost = driver.page_source
    soup_otchetnost = BeautifulSoup(page_source_otchetnost, 'html.parser')

    # Находим блок с отчетностью
    otchetnost_block = soup_otchetnost.find('ul', {'style': 'list-style-type: none;'})

    # Получаем последний отчет
    last_otchetnost_item = otchetnost_block.find('li')

    # Получаем информацию о последнем отчете
    last_otchetnost_name = last_otchetnost_item.text.strip()
    last_otchetnost_relative_link = last_otchetnost_item.a['href']

    # Формируем абсолютную ссылку
    last_otchetnost_full_link = urljoin(base_url, last_otchetnost_relative_link)

    # Получаем текущую дату в формате "дд.мм.гггг"
    current_date_str = datetime.now().strftime("%d.%m.%Y")

    # Переходим по ссылке последнего отчета
    driver.get(last_otchetnost_full_link)

    # Ждем, пока появится таблица с информацией о документах (ждем не более 30 секунд)
    try:
        table_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.zebra.noBorderTbl.centerHeader.files-table')))
    except TimeoutException:
        print(f"Таблица с информацией о документах не была найдена на странице {last_otchetnost_full_link}")
        driver.quit()
        return {"company_name": company_link_element.text.strip(), "reports": []}

    # Получаем все строки таблицы
    rows = table_element.find_elements(By.TAG_NAME, 'tr')

    # Пропускаем заголовок таблицы (первую строку)
    # Получаем ячейки строки
    cells = rows[1].find_elements(By.TAG_NAME, 'td')

    # Извлекаем информацию
    if len(cells) >= 6:  # Удостоверимся, что в строке есть необходимые ячейки
        document_type = cells[1].text.strip()

        # Извлекаем дату размещения
        approval_date_cell = cells[4].text.strip()

        # Пробуем извлечь дату из строки
        try:
            approval_date = datetime.strptime(approval_date_cell, "%d.%m.%Y").strftime("%d.%m.%Y %H:%M")
        except ValueError:
            # Если не удается преобразовать дату, используем исходный текст
            approval_date = approval_date_cell

        # Формируем данные о последнем отчете
        last_report = {
            "otchetnost_name": last_otchetnost_name,
            "document_type": document_type,
            "approval_date": approval_date,
            "link": last_otchetnost_full_link
        }

    # Закрываем браузер
    driver.quit()

    # Возвращаем результат в виде словаря
    if last_report:
        reports_data = {
            "company_name": company_link_element.text.strip(),
            "reports": [last_report]
        }
        print(reports_data)
        return reports_data
    else:
        return {"company_name": company_link_element.text.strip(), "reports": []}
