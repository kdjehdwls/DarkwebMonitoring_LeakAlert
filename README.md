# DarkwebMonitoring_LeakAlert
**OSINT 딥다크 웹 모니터링 및 알림 프로젝트**

**1. 웹서비스로 배포**

- Leakbase, Lockbit, Blacksuit 사이트에서 크롤링한 Leaked Data 게시
- 키워드 검색으로 필터링

![Web.png](https://github.com/kdjehdwls/DarkwebMonitoring_LeakAlert/blob/master/img/Web.png)



**2. 유출 데이터 알람**

- 서버에서 스케쥴링을 활용하여 주기적으로 cwaler.py를 실행
- db에 새로운 유출데이터 업데이트 (update_db.py)
- 새로운 유출데이터 Slack 알람 (slack_alarm.py)

![Slack_alert.png](https://github.com/kdjehdwls/DarkwebMonitoring_LeakAlert/blob/master/img/Slack_alert.png)



**3. 시연 영상**


<img width="80%" src="https://github.com/kdjehdwls/DarkwebMonitoring_LeakAlert/assets/50543442/e0189056-639e-446f-ab1d-6af62887fdf9"/>

**[🔗시연영상 링크](https://youtu.be/f5bUuweKXko)**
