from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['instagram_users']
user = 'bokolyarkonstantin'


def db_search_friendship(username, type):
    docs = []
    for doc in db.get_collection(f'{username}_{type}').find({}):
        docs.append(doc)
    return docs


followers = db_search_friendship(user, type='followers')
followings = db_search_friendship(user, type='followings')
print(f'followers: {followers}')
print(f'followins: {followings}')
