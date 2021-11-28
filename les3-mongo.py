#https://tula.hh.ru/search/vacancy?text=1c+консультант&area=92&fromSearchLine=false
#https://tula.hh.ru/search/vacancy?clusters=true&area=92&ored_clusters=true&enable_snippets=true&salary=&text=1c+консультант
#https://tula.hh.ru/search/vacancy?clusters=true&area=92&ored_clusters=true&enable_snippets=true&text=1c+консультант


from pprint import pprint
import requests
from bs4 import BeautifulSoup
import re
import json
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['hh_vacation']
dbvacations = db.vacations

url = 'https://tula.hh.ru'
page = 0
params = {'cluster': 'true',
          'area': '92',
          'ored_clusters': 'true',
          'enable_snippets': 'true',
          'text': 'консультант',
          'page': f'{page}',
          'items_on_page': '20'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36'}
response = requests.get(url + '/search/vacancy', params=params, headers=headers)
#response = requests.get('https://tula.hh.ru/search/vacancy?clusters=true&area=92&ored_clusters=true&enable_snippets=true&text=1c+консультант', headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')
resumes = dom.find_all('div', {'class': 'vacancy-serp-item'})
vacations = []

n = 0
while True:
    is_page_number_final = dom.find(text='дальше')
    try:
        is_page_number_final1 = dom.find(text='дальше').parent.parent['data-qa']
    except:
        is_page_number_final1 = None
    if page != 0:
        params = {'cluster': 'true',
                'area': '92',
                'ored_clusters': 'true',
                'enable_snippets': 'true',
                'text': 'консультант',
                'page': f'{page}',
                'items_on_page': '20'}
        response = requests.get(url + '/search/vacancy', params=params, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        resumes = dom.find_all('div', {'class': 'vacancy-serp-item'})
    for resume in resumes:
        vacation_data = {}
        position = resume.find('span', {'data-qa': 'bloko-header-3'}).getText()
        compensation = resume.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        link = resume.find('a')['href']
        salary_min = None
        salary_max = None
        salary_cur = None
        try:
            compensation = compensation.getText().replace(b'\xe2\x80\xaf'.decode(), '')
            if 'от' in compensation.split(' '):
                salary_min = float(re.search(r'\d+', compensation).group())
            elif 'до' in compensation.split(' '):
                salary_max = float(re.search(r'\d+', compensation).group())
            elif '–' in compensation.split(' '):
                salary_min = float(re.match(r'\d+', compensation).group())
                salary_max = float(re.search(r' \d+', compensation).group())
            salary_cur = re.search(r'\D+$', compensation).group().strip()
        except:
            compensation = None

        #real_link +id

        response1 = requests.get(link, headers=headers)
        vacation_id_temp = response1.url
        real_link = vacation_id_temp[:vacation_id_temp.find('?')]
        vacation_id = real_link.split('/')[-1]
        #
        vacation_data['_id'] = vacation_id
        vacation_data['position'] = position
        vacation_data['salary_min'] = salary_min
        vacation_data['salary_max'] = salary_max
        vacation_data['salary_cur'] = salary_cur
        vacation_data['link'] = real_link
        vacation_data['site'] = 'https://hh.ru'
        i = 0

        for doc in dbvacations.find({'_id': vacation_id}):
            i = 1
        #print(i)
        if i == 0:
            dbvacations.insert_one(vacation_data)
            n += 1
        #pprint(vacation_data)
    page += 1
    if is_page_number_final is not None and is_page_number_final1 == 'pager-next':
        continue
    else:
        break

print(f'Добавлено новых {n} вакансий')



