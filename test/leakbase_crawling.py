import requests
import pytz
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

token = 'token'
channel = 'channel'
file_path = 'leakbase_clean.json'
leakbase_url = 'https://leakbase.io/'


# 슬랙 알림 전송
def slack_alarm(post):
    text = f"New post\nTitle: {post['title']}\nUpload time: {post['upload time']}\nAuthor: {post['author']}\nURL: {post['url']}"
    requests.post('https://slack.com/api/chat.postMessage', 
    headers = {"Authorization": "Bearer "+token},
    data={"channel":channel,"text":text})

# 파일 업데이트
def update_file(posts):
    crawled_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path,'w',encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
        
        print(f'{file_path} updated.')

# 이전 게시글 데이터 불러오기
def load_previous_posts(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:  # UTF-8 인코딩을 명시적으로 지정
            return json.load(file)
    except FileNotFoundError:
        return []


# 새로운 게시글 확인 및 처리
def check_posts(new_posts):
    previous_posts = load_previous_posts('leakbase_clean.json')
    if not previous_posts:
        for post in new_posts:
            slack_alarm(post)
        update_file(new_posts)
        return
    
    previous_urls = set(post['url'] for post in previous_posts)
    new_posts_found = [post for post in new_posts if post['url'] not in previous_urls]

    if new_posts_found:
        for post in reversed(new_posts_found): # 슬랙 알림 과거-최신순으로 보내도록
            slack_alarm(post)
        updated_posts = new_posts_found + previous_posts
        update_file(updated_posts)
    else:
        update_file(previous_posts)        

# Leakbase 데이터 가져오기
def fetch_leakbase_data():
    response = requests.get(leakbase_url)
    if response.status_code == 200:    
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
        check_posts(posts)
    else:
        print("Failed to fetch data from Leakbase.")

if __name__ == "__main__":
    fetch_leakbase_data()