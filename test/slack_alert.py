from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack Bot Token 설정
slack_token = "slack_token"

# Slack WebClient 초기화
client = WebClient(token=slack_token)

# 메시지를 보낼 채널 ID 설정
channel_id = "channel_id"

# 보낼 메시지 내용 설정
message = "안녕하세요! 슬랙 알림봇입니다."

# Slack에 메시지 보내는 함수
def send_message(channel, message):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print("Message sent:", response["message"]["text"])
    except SlackApiError as e:
        print("Error sending message:", e.response["error"])

# 메시지 보내기
send_message(channel_id, message)