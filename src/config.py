import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 환경 변수 할당
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
LEAKBASE_FILE_PATH = os.getenv('LEAKBASE_FILE_PATH')
LOCKBIT_FILE_PATH = os.getenv('LOCKBIT_FILE_PATH')
BLACKSUIT_FILE_PATH = os.getenv('BLACKSUIT_FILE_PATH')
PROXY_SERVER = os.getenv('PROXY_SERVER')
