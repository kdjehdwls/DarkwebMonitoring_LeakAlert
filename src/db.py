from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db_leakbase = client['leakbase']
db_lockbit = client['lockbit']
db_blacksuit = client['blacksuit']
collection_leakbase = db_leakbase['posts']
collection_lockbit = db_lockbit['posts']
collection_blacksuit = db_blacksuit['posts']

def get_leakbase_posts():
    return list(collection_leakbase.find({}).sort('_id',-1))

def get_lockbit_posts():
    return list(collection_lockbit.find({}).sort('id',-1))

def get_blacksuit_posts():
    return list(collection_blacksuit.find({}).sort('id',-1))
