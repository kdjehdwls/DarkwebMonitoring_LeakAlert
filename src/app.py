from flask import Flask, render_template
from db import get_leakbase_posts, get_lockbit_posts, get_blacksuit_posts

app = Flask(__name__)

@app.route('/')
def index():
    # MongoDB에서 데이터 가져오기
    leakbase_posts = get_leakbase_posts()
    lockbit_posts = get_lockbit_posts()
    blacksuit_posts = get_blacksuit_posts()
    # 템플릿에 데이터 전달
    return render_template('index.html', leakbase_posts=leakbase_posts, lockbit_posts=lockbit_posts, blacksuit_posts=blacksuit_posts)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
