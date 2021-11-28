from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['hh_vacation']
dbvacations = db.vacations

def db_search(min_salary):
    i = 0
    for doc in dbvacations.find({'$or': [
                                        {'salary_min': {'$gte': min_salary} },
                                        {'salary_max': {'$gte': min_salary} }
                                ]}):
        pprint(doc)
        i += 1
    #    print('x')
    print(i)


db_search(120000)
