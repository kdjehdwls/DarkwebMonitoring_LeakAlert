from config import SLACK_TOKEN, SLACK_CHANNEL
import requests

def slack_alarm(post, site):
    if site == 'lockbit':
        text = f"🚨 Data Breach Alert from Lockbit 🚨\nTitle: {post['title']}\nDetails: {post['post_text']}\nUpload time: {post['upload time']}\n⏳ days: {post['days']}\n URL: {post['url']}"
    elif site == 'leakbase':
        text = f"🚨 Data Breach Alert from Leakbase🚨\nTitle: {post['title']}\nUpload time: {post['upload time']}\nAuthor: {post['author']}\nURL: {post['url']}"
    elif site == 'blacksuit':
        urls_text = '\n'.join([f"{url['url-title']}: {url['url-link']}" for url in post['url']])
        text = f"🚨 Data Breach Alert from Blacksuit🚨\nTitle: {post['title']}\nDetails: {post['post-text']}\nURLs:\n{urls_text}"
    else:
        print("Slack Alarm Error")
    
    requests.post('https://slack.com/api/chat.postMessage', 
    headers = {"Authorization": "Bearer "+SLACK_TOKEN},
    data={"channel":SLACK_CHANNEL,"text":text})
    pass
