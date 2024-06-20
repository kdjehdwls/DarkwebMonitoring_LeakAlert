import pytz
import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from webdriver_setting import open_driver
# from storage import check_posts
from selenium.common.exceptions import TimeoutException, WebDriverException
from requests.exceptions import RequestException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from config import LEAKBASE_FILE_PATH, LOCKBIT_FILE_PATH, BLACKSUIT_FILE_PATH
import json
from slack_alarm import slack_alarm


# 이전 게시글 데이터 불러오기
def load_previous_posts(site):
    if site == 'leakbase':
        file_path = LEAKBASE_FILE_PATH
    elif site == 'lockbit':
        file_path = LOCKBIT_FILE_PATH
    elif site == 'blacksuit':
        file_path = BLACKSUIT_FILE_PATH

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            previous_posts = json.load(file)
    except FileNotFoundError:
        previous_posts = []
    return previous_posts

# 새로운 게시글 확인 및 처리
def check_posts(new_posts, site):
    previous_posts = load_previous_posts(site)
    if not previous_posts:
        for post in new_posts:
            slack_alarm(post, site)
        update_file(new_posts, site)
        return
    
    if site == 'leakbase':
        previous_urls = set(post['url'] for post in previous_posts)
        new_posts_found = [post for post in new_posts if post['url'] not in previous_urls]
    elif site == 'lockbit':
        previous_urls = set(post['title'] for post in previous_posts)
        new_posts_found = [post for post in new_posts if post['title'] not in previous_urls]
    elif site == 'blacksuit':
        previous_urls = set(post['title'] for post in previous_posts)
        new_posts_found = [post for post in new_posts if post['title'] not in previous_urls]
    else:
        print('Error')
        return
    
    if new_posts_found:
        for post in reversed(new_posts_found): # 슬랙 알림 과거-최신순으로 보내도록
            slack_alarm(post, site)
        updated_posts = new_posts_found + previous_posts
        update_file(updated_posts, site)
    else:
        update_file(previous_posts, site)


# 파일 업데이트
def update_file(posts, site):
    # crawled_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if site == 'leakbase':
        file_path = LEAKBASE_FILE_PATH
    elif site == 'lockbit':
        file_path = LOCKBIT_FILE_PATH
    elif site == 'blacksuit':
        file_path = BLACKSUIT_FILE_PATH  
    with open(file_path,'w',encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
        
        print(f'json file path: {file_path} updated.')

# URL 페이지를 가져와 파싱, 타임아웃 발생시 브라우저 종료하고 예외 발생
def fetch_and_parse_html(driver, url, wait_element=None):
    try:
        driver.get(url)
        if wait_element:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_element))
            )
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
            print(f"타임아웃 에러 발생 URL: {url}. 다시 시도해주시길 바랍니다.")
            raise TimeoutException(f"Failed to load {url}, browser closed.")


# leakbase
def fetch_leakbase_data():
    site = 'leakbase'
    leakbase_url = 'https://leakbase.io/'

    try:
        response = requests.get(leakbase_url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
    
        # 게시글 정보 추출
        post_elements = soup.select('div._xgtIstatistik-satir--konu')
        time_elements = soup.select('time.structItem-latestDate')
        forum_elements = [a['title'] for a in soup.select('._xgtIstatistik-satir--hucre._xgtIstatistik-satir--forum a[title]')]

        posts = []

        for post_element, time_element, forum in zip(post_elements, time_elements, forum_elements):
            # 작성자 정보
            author = post_element.get('data-author', 'no author')
            # url
            title_tag = post_element.find('a', attrs={'data-preview-url': True})            
            # 게시글 시간정보
            datetime_str = time_element.get('datetime', 'no time info')
            utc_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
            korea_datetime_str = utc_datetime.astimezone(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
            time_text = time_element.get_text().strip()
        
            # 게시글 주소
            if title_tag:
                full_url = urljoin(leakbase_url, title_tag['href'])
                title = title_tag.get_text().strip()
                
                post_data = {
                    'title': title,
                    'upload time': korea_datetime_str,
                    'time_text': time_text,
                    'author': author,
                    'url': full_url
                }
                posts.append(post_data)
        
        # 새로운 게시글 확인 및 처리
        check_posts(posts, site)
    except RequestException as e:
        print(f'Request to {leakbase_url} failed: {e}')

# lockbit
def fetch_lockbit_data():
    site = 'lockbit'
    driver = open_driver()
    URL = "http://lockbit7ouvrsdgtojeoj5hvu6bljqtghitekwpdy3b6y62ixtsu5jqd.onion"

    try:
        soup = fetch_and_parse_html(driver, URL)

        posts = []

        post_container = soup.find('div', class_='post-big-list')
        if post_container:
            post_blocks = post_container.find_all('a', class_='post-block')

            for post in post_blocks:
                title = post.find('div', class_='post-title').text.strip()
                post_text = post.find('div', class_='post-block-text').text.strip()
                updated_date = post.find('div', class_='updated-post-date').text.strip()
                days_element = post.find('span', class_='days')
                post_url = post.get('href')
                full_url = urljoin(URL, post_url)
                if days_element:
                    days = days_element.text.strip()
                else:
                    days = 'published'
                
                post_data = {
                    'title': title,
                    'post_text': post_text,
                    'upload time': updated_date,
                    'days': days,
                    'url': full_url
                }
                posts.append(post_data)

        check_posts(posts, site)
    except (TimeoutException, WebDriverException) as e:
        print(f'An error occurred: {e}')
    finally:
        driver.quit()

def fetch_blacksuit_data():      
    site = 'blacksuit'
    driver = open_driver()
    URL = "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"
    current_page_number = 1
    posts = []  # 포스트 리스트를 루프 밖에 위치
    
    try:
        while True:
            soup = fetch_and_parse_html(driver, f"{URL}/?page={current_page_number}")
            post_container = soup.find('main')
            
            if post_container:
                post_blocks = post_container.find_all('div', class_='card')
                
                for post in post_blocks:
                    try:
                        title = post.find('div', class_='url').find('a')['href'].strip()
                        post_text = post.find('div', class_='text').text.strip()        
                        links = []
                        link_div = post.find('div', class_='links')
                        
                        if link_div:
                            for lk in link_div.find_all('a'):
                                url_title = lk.text.strip()
                                url_link = lk['href']
                                
                                links.append({
                                    'url-title': url_title,
                                    'url-link': url_link,
                                })

                        post_data = {
                            'title': title,
                            'post-text': post_text,
                            'url': links,
                        } 
                        
                        posts.append(post_data)  # 포스트 데이터를 포스트 리스트에 추가
                        
                    except (TimeoutException, WebDriverException) as e:
                        print(f'An error occurred: {e}')
            
            pagination_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a")
            if pagination_links and current_page_number < int(pagination_links[-1].text):
                current_page_number += 1
            else:
                break
        check_posts(posts, site)
    
    
    except (TimeoutException, WebDriverException) as e:
        print(f'An error occurred: {e}')
    
    finally:
        driver.quit()
