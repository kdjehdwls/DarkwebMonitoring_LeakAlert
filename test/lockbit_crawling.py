from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import requests
from datetime import datetime
import json
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

token = 'token'
channel = 'channel'
file_path = r'D:\Git\goorm_crawler\lockbit_clean.json'

# Selenium을 사용하여 Chrome 웹 드라이버를 설정하고 반환
def open_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

    # Service 객체를 사용하여 ChromeDriver의 경로를 설정합니다.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options) 
    driver.set_page_load_timeout(300)

    return driver

# URL 페이지를 가져와 파싱, 타임아웃 발생시 브라우저 종료하고 예외 발생
def fetch_and_parse_html(driver, url):
    try:
        driver.get(url)
        time.sleep(20)  
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
            print(f"타임아웃 에러 발생 URL: {url}. 다시 시도해주시길 바랍니다.")
            driver.quit()  
            raise TimeoutException(f"Failed to load {url}, browser closed.")

# 슬랙 알림 전송
def slack_alarm(post):
    text = f"New post\nTitle: {post['title']}\npost_text: {post['post_text']}\nupload time: {post['upload time']}\ndays: {post['days']}"
    requests.post('https://slack.com/api/chat.postMessage', 
    headers = {"Authorization": "Bearer "+token},
    data={"channel":channel,"text":text})

# 파일 업데이트
def update_file(posts):
    crawled_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path,'w',encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
        
        print(f'{file_path} updated at {crawled_time}')

# 이전 게시글 데이터 불러오기
def load_previous_posts():
    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            previous_posts = json.load(file)
    except FileNotFoundError:
        previous_posts = []
    return previous_posts


# 새로운 게시글 확인 및 처리
def check_posts(new_posts):
    previous_posts = load_previous_posts()
    if not previous_posts:
        for post in new_posts:
            slack_alarm(post)
        update_file(new_posts)
        return
    
    previous_urls = set(post['title'] for post in previous_posts)
    new_posts_found = [post for post in new_posts if post['title'] not in previous_urls]

    if new_posts_found:
        for post in reversed(new_posts_found): # 슬랙 알림 과거-최신순으로 보내도록
            slack_alarm(post)
        updated_posts = new_posts_found + previous_posts
        update_file(updated_posts)
    else:
        update_file(previous_posts)   

# LockBit 데이터 가져오기
def main():
    driver = open_driver()
    URL = "http://lockbit7ouvrsdgtojeoj5hvu6bljqtghitekwpdy3b6y62ixtsu5jqd.onion"
    soup = fetch_and_parse_html(driver, URL)

    posts = []

    post_container = soup.find('div', class_='post-big-list')
    if post_container:
        post_blocks = post_container.find_all('a', class_='post-block')

        for post in post_blocks:
            title = post.find('div', class_='post-title').text.strip()
            post_text = post.find('div', class_='post-block-text').text.strip()
            updated_date = post.find('div', class_='updated-post-date').text.strip()
            #victim = "".join(x for x in title if x.isalnum() or x.isspace())
            days_element = post.find('span', class_='days')
            if days_element:
                days = days_element.text.strip()
            else:
                days = 'published'
            
            post_data = {
                'title': title,
                'post_text': post_text,
                'upload time': updated_date,
                'days': days,
                #'url': full_url
            }
            posts.append(post_data)

    check_posts(posts)
    driver.quit()


if __name__ == '__main__':
    main()
