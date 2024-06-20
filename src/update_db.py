from pymongo import MongoClient
import json

# MongoDB 설정
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
LEAKBASE_DB_NAME = 'leakbase'
LOCKBIT_DB_NAME = 'lockbit'
BLACKSUIT_DB_NAME = 'blacksuit'
COLLECTION_NAME = 'posts'

def update_database(file_path, database_name, main_field):
    # MongoDB 클라이언트 생성
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[database_name]
    collection = db[COLLECTION_NAME]

    # JSON 파일 로드
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # MongoDB에 데이터 업데이트
    for item in data:
        # MongoDB에서 동일한 'url'을 가진 문서를 찾아 업데이트하거나, 존재하지 않는 경우 새로운 문서 추가
        collection.update_one({main_field: item[main_field]}, {'$set': item}, upsert=True)

    print("Database has been updated.")

# 스크립트 실행
if __name__ == "__main__":
    update_database('/home/ubuntu/crawler/data/leakbase_data.json', LEAKBASE_DB_NAME,'url')  
    update_database('/home/ubuntu/crawler/data/lockbit_data.json', LOCKBIT_DB_NAME,'title')
    update_database('/home/ubuntu/crawler/data/blacksuit_data.json',BLACKSUIT_DB_NAME,'title')
