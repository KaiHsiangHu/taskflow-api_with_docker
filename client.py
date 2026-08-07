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


## ==================== without requests ======================== ##
# import json
# from urllib.request import Request, urlopen


# BASE_URL = "http://127.0.0.1:8000"


# def get_tasks():
#     """GET：取得全部待辦事項。"""
#     with urlopen(f"{BASE_URL}/api/tasks") as response:
#         return json.load(response)


# def create_task(title):
#     """POST：新增待辦事項。"""
#     body = json.dumps(
#         {"title": title},
#         ensure_ascii=False,
#     ).encode("utf-8")

#     request = Request(
#         f"{BASE_URL}/api/tasks",
#         data=body,
#         method="POST",
#         headers={"Content-Type": "application/json"},
#     )

#     with urlopen(request) as response:
#         return json.load(response)


# if __name__ == "__main__":
#     print("目前的待辦事項：")

#     tasks = get_tasks()
#     for task in tasks:
#         print(task)

#     print("\n新增待辦事項：")

#     new_task = create_task("使用 Python 呼叫 POST API")
#     print(new_task)

#     print("\n更新後的待辦事項：")

#     tasks = get_tasks()
#     for task in tasks:
#         print(task)


## ==================== with requests ======================== ##
import os

import requests


BASE_URL = "http://127.0.0.1:8000"
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

