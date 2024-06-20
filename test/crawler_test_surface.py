import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack Bot Token 설정
slack_token = "slack_token"

# Slack WebClient 초기화
client = WebClient(token=slack_token)

# 메시지를 보낼 채널 ID 설정
channel_id = "channel_id"

def crawl_wikipedia(url):
    # 웹 페이지에 GET 요청을 보냅니다.
    response = requests.get(url)
    
    # 요청이 성공하면 HTML 코드를 추출합니다.
    if response.status_code == 200:
        html = response.text
        
        # BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
        soup = BeautifulSoup(html, 'html.parser')
        
        # 제목과 본문을 추출합니다.
        title = soup.find('h1', {'class': 'firstHeading'}).text
        content_paragraphs = soup.find('div', {'class': 'mw-parser-output'}).find_all('p')
        content = '\n'.join([p.text for p in content_paragraphs])
        
        return title, content
    else:
        print("Error: Failed to retrieve page")
        return None, None

if __name__ == "__main__":
    # 크롤링할 Wikipedia 페이지의 URL을 지정합니다.
    wikipedia_url = "https://en.wikipedia.org/wiki/Web_scraping"
    
    # crawl_wikipedia 함수를 사용하여 페이지에서 제목과 본문을 추출합니다.
    title, content = crawl_wikipedia(wikipedia_url)
    
    # 제목과 본문을 출력합니다.
    if title and content:
        message = ("title : " + title)
        message = ("content : " + content)
    else:
        print("Failed to crawl Wikipedia page")

# Slack에 메시지 보내는 함수
def send_message(channel, message):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print("Message sent:", response["message"]["text"])
    except SlackApiError as e:
        print("Error sending message:", e.response["error"])

# 메시지 보내기
send_message(channel_id, message)