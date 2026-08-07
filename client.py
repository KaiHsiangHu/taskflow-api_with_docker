## ==================== with power shell ======================== ##
# # GET：取得資料
# 取得所有待辦事項：
# Invoke-RestMethod `
#   -Method Get `
#   -Uri "http://127.0.0.1:8000/api/tasks"


# # 測試健康檢查：
# Invoke-RestMethod `
#   -Method Get `
#   -Uri "http://127.0.0.1:8000/api/health"


# # POST：新增資料
# Invoke-RestMethod `
#   -Method Post `
#   -Uri "http://127.0.0.1:8000/api/tasks" `
#   -ContentType "application/json" `
#   -Body '{"title":"練習 POST API"}'


## ============================================ ##
import os

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
PASSWORD = os.environ.get("APP_PASSWORD", "taskflow123")
session = requests.Session()


# 登入並保存後端回傳的 Session Cookie
response = session.post(
    f"{BASE_URL}/api/login",
    json={"password": PASSWORD},
    timeout=10,
)
response.raise_for_status()
print("登入成功")


# GET
response = session.get(
    f"{BASE_URL}/api/tasks",
    timeout=10,
)
response.raise_for_status()

tasks = response.json()
print(tasks)


# POST
response = session.post(
    f"{BASE_URL}/api/tasks",
    json={"title": "使用 requests 呼叫 API"},
    timeout=10,
)
response.raise_for_status()

new_task = response.json()
print(new_task)


# 第二、第三分頁：將測試操作同步到目前開啟的網頁
response = session.post(
    f"{BASE_URL}/api/demo-state",
    json={
        "active_tab": "ai",
        "selected_signs": ["capricorn", "virgo"],
        "month": 12,
        "day": 24,
        "focus": "星座的人格特質",
        "refresh_tasks": True,
        "generate_ai": True,
    },
    timeout=10,
)
response.raise_for_status()

print("第二分頁：已勾選摩羯座和處女座")
print("第三分頁：已填入 12 月 24 日，以及『星座的人格特質』")
print("第三分頁：已執行『產生 AI 解讀』")
print("請查看已開啟的網頁；畫面會在一秒內同步。")
