# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pprint import pprint
from pymongo import MongoClient

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram_users

    def process_item(self, item, spider):
        el = {}
        el['_id'] = item['f_user_id']
        el['username'] = item['f_username']
        el['photo'] = item['f_user_photo']
        # followers.append(item)
        if item['type'] == 'follower':
            collection = self.mongo_base[f"{item['username']}_followers"]
            i = 0
            for doc in collection.find({'_id': el['_id']}):
                i = 1
            if i == 0:
                collection.insert_one(el)
        if item['type'] == 'following':
            collection = self.mongo_base[f"{item['username']}_followings"]
            i = 0
            for doc in collection.find({'_id': el['_id']}):
                i = 1
            if i == 0:
                collection.insert_one(el)
        return item
