from lxml import html
from pprint import pprint
import requests

from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['lenta_news']
dbnews = db.news

url = 'https://lenta.ru'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36'}
response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)

news = dom.xpath("//section[contains(@class, 'b-top7-for-main')]//div[contains(@class, 'item')]")
news_list = []

for news_item in news:
    news_dict = {}
    news_name = news_item.xpath(".//a/text()")
    news_link = news_item.xpath(".//a/@href")
    news_date = news_item.xpath(".//time[@class='g-time']/@datetime")
    news_author = url

    news_dict['news_name'] = news_name[0].replace(u'\xa0', ' ')
    news_dict['news_link'] = url+news_link[0]
    news_dict['news_date'] = news_date[0]
    news_dict['news_author'] = news_author

    news_list.append(news_dict)

#pprint(news_list)

n = 0
for news_item in news_list:
    i = 0
    for db_news_item in dbnews.find({'news_link': news_item['news_link']}):
        i = 1
    if i == 0:
        dbnews.insert_one(news_item)
        n += 1

print(f'Добавлено новых {n} новостей')


for db_news_item in dbnews.find({}):
    pprint(db_news_item)