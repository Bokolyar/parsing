# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            final_salary = self.process_salary_hhru(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            item['salary_type'] = final_salary[3]
            final_url = self.process_link_hhru(item['url'])
            item['url'] = final_url[0]
            item['_id'] = final_url[1]
        elif spider.name == 'sjru':
            final_salary = self.process_salary_sjru(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            item['_id'] = item['url']
        del item['salary']
        collection = self.mongo_base[spider.name]
        i = 0
        for doc in collection.find({'_id': item['_id']}):
            i = 1
        if i == 0:
            collection.insert_one(item)

        return item

    def process_salary_hhru(self, salary):
        if 'з/п не указана' in salary[0] or (not salary):
            min = None
            max = None
            cur = None
            s_type = None
        elif 'от' in salary[0]:
            min = float(salary[1].replace('\xa0', ''))
            if 'до' in salary[2]:
                max = float(salary[3].replace('\xa0', ''))
            else:
                max = None
            cur = salary[-2]
            if 'на руки' in salary[-1]:
                s_type = 'net'
            else:
                s_type = 'gross'
        elif 'до' in salary[0]:
            min = None
            max = float(salary[1].replace('\xa0', ''))
            cur = salary[-2]
            if 'на руки' in salary[-1]:
                s_type = 'net'
            else:
                s_type = 'gross'
        return min, max, cur, s_type

    def process_link_hhru(self, link):
        vacation_id_temp = link
        real_link = vacation_id_temp[:vacation_id_temp.find('?')]
        vacation_id = real_link.split('/')[-1]
        return real_link, vacation_id

    def process_salary_sjru(self, salary):
        if 'По договорённости' in salary:
            min = None
            max = None
            cur = None
        elif 'от' in salary:
            min = float(''.join(salary[2].split('\xa0')[:-1]))
            max = None
            cur = salary[2].split('\xa0')[-1]
        elif 'до' in salary:
            min = None
            max = float(''.join(salary[2].split('\xa0')[:-1]))
            cur = salary[2].split('\xa0')[-1]
        elif len(salary) == 3:
            min = float(salary[0].replace('\xa0', ''))
            max = min
            cur = salary[-1]
        else:
            min = float(salary[0].replace('\xa0', ''))
            max = float(salary[4].replace('\xa0', ''))
            cur = salary[-1]
        return min, max, cur