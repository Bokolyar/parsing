import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint

from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta

url = "https://www.mail.ru"
driver = webdriver.Firefox()
driver.maximize_window()
driver.implicitly_wait(15)
driver.get(url)

elem = driver.find_element(By.NAME, 'login')
elem.send_keys('study.ai_172@mail.ru')

elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.NAME, 'password')
WebDriverWait(driver, 10).until(EC.visibility_of(elem))
#elem = driver.find_element(By.NAME, 'password')
elem.send_keys('NextPassword172#')

elem.send_keys(Keys.ENTER)

emails_list = []

while True:
    emails = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")
    if emails[-1].get_attribute('data-uidl-id') in [emails_list[i]['email_id'] for i in range(len(emails_list))]:
        break
    # len(emails)
    for email_unit in emails:
        emails_dict = {}
        if email_unit.get_attribute('data-uidl-id') in [emails_list[i]['email_id'] for i in range(len(emails_list))]:
            continue
        emails_dict['email_id'] = email_unit.get_attribute('data-uidl-id')
        emails_dict['email_link'] = email_unit.get_attribute('href')
#        email_from = email_unit.find_element(By.CLASS_NAME, 'll-crpt').get_attribute('title')

        emails_list.append(emails_dict)
    elem = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")
    try:
        elem[-1].send_keys(Keys.PAGE_DOWN)
    except:
        break
    time.sleep(1)

emails_list.pop()
# pprint(emails_list)

client = MongoClient('127.0.0.1', 27017)
db = client['mail_ru']
dbmail = db.mail

n = 0
for mail_item in emails_list:
    i = 0
    for db_mail_item in dbmail.find({'_id': mail_item['email_id']}):
        i = 1
    if i == 0:
        dict = {}
        url = mail_item['email_link']
        driver.get(url)
        dict['_id'] = mail_item['email_id']
        dict['email_link'] = url
        dict['email_from'] = driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title')
        date = driver.find_element(By.CLASS_NAME, 'letter__date').text
        if date.split(',')[0] == 'Сегодня':
            date = datetime.today().strftime('%d-%m-%Y') + ',' + date.split(',')[1]
        elif date.split(',')[0] == 'Вчера':
            date_temp = datetime.today() - timedelta(days=1)
            date = date_temp.strftime('%d-%m-%Y') + ',' + date.split(',')[1]
        else:
            time = date.split(',')[1]
            date_temp = date.split(',')[0]
            day = int(date_temp.split(' ')[0])
            month_temp = date_temp.split(' ')[1]
            month = 12 if month_temp == 'декабря' else (
                        11 if month_temp == 'ноября' else (
                            10 if month_temp == 'октября' else (
                                9 if month_temp == 'сентября' else (
                                    8 if month_temp == 'августа' else (
                                        7 if month_temp == 'июля' else (
                                            6 if month_temp == 'июня' else (
                                                5 if month_temp == 'мая' else (
                                                    4 if month_temp == 'апреля' else (
                                                        3 if month_temp == 'марта' else (
                                                            2 if month_temp == 'февраля' else 1))))))))))
            year = 2021
            date = datetime(day=day, month=month, year=year).strftime('%d-%m-%Y') + ',' + time
        dict['email_date'] = date
        dict['email_subject'] = driver.find_element(By.CLASS_NAME, 'thread__subject').text
        dict['email_body'] = driver.find_element(By.CLASS_NAME, 'letter__body').text

        dbmail.insert_one(dict)
        n += 1

print(f'Добавлено новых {n} писем')
driver.quit()
