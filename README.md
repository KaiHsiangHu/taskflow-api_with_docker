# 前後端 REST API 範例

這是一個不需安裝第三方套件的待辦事項範例。後端為 Python REST API，前端為原生 HTML、CSS 與 JavaScript；資料暫存在記憶體，重新啟動後會還原。

## 使用 Docker 啟動

先安裝並啟動 Docker Desktop，在專案根目錄執行：

```powershell
docker compose up --build
```

開啟 <http://127.0.0.1:8000>。停止服務可按 `Ctrl+C`，或執行 `docker compose down`。

也可以不使用 Compose：

```powershell
docker build -t taskflow-api .
docker run --rm -p 8000:8000 --env-file .env taskflow-api
```

`.dockerignore` 會避免 `.env`、Git 資料、測試及快取被複製進映像，因此密碼與 API Key 不會寫入映像檔。

## 部署到 Render（Docker）

1. 將包含 `Dockerfile`、`.dockerignore`、`compose.yaml` 與 `render.yaml` 的專案推送到 GitHub。
2. 在 Render Dashboard 選 **New > Blueprint**，連接此 GitHub repository；Render 會依 `render.yaml` 建立 Docker Web Service。
3. 建立時填入 Secret `APP_PASSWORD` 與 `GEMINI_API_KEY`；若不使用 Gemini，後者可留空。
4. 部署完成後測試 `https://你的服務網址/api/health`。

之後每次推送到所連接的分支，Render 都會重新使用 Dockerfile 建置和部署。Render 會自行提供 `PORT`，程式已會讀取；Dockerfile 也已讓服務監聽容器所需的 `0.0.0.0`。

若不使用 Blueprint，也可選 **New > Web Service**、連接 GitHub，Language/Runtime 選 **Docker**；Dockerfile Path 使用 `./Dockerfile`，Health Check Path 使用 `/api/health`。不需再填 Python Build Command 或 Start Command。

### 常用 Docker 指令

| 指令 | 用途 |
|---|---|
| `docker compose up --build` | 建置映像並在本機啟動服務 |
| `docker compose up -d --build` | 在背景建置並啟動 |
| `docker compose logs -f` | 持續查看容器日誌 |
| `docker compose ps` | 查看服務狀態 |
| `docker compose down` | 停止並移除 Compose 容器與網路 |
| `docker build -t taskflow-api .` | 只建置名為 `taskflow-api` 的映像 |
| `docker run --rm -p 8000:8000 --env-file .env taskflow-api` | 直接從映像啟動容器 |
| `docker images` | 列出本機映像 |
| `docker ps` | 列出執行中的容器 |

## 不使用 Docker 的本機啟動

在專案根目錄執行：

```powershell
py server.py
```

然後開啟 <http://127.0.0.1:8000>。也可以在 VS Code 的「執行與偵錯」選擇 **啟動前後端 API 範例**。

## 設定登入密碼

第一次使用時，安裝相依套件：

```powershell
conda install python-dotenv requests
```

接著修改專案第一層的 `.env`：

```dotenv
APP_PASSWORD=換成你的密碼
GEMINI_API_KEY=貼上你的 Google AI Studio API Key
GEMINI_MODEL=gemini-3.5-flash-lite
```

直接執行 `python server.py` 時，程式會自動讀取 `.env`。這個檔案已被 `.gitignore` 排除，不會推送到 GitHub；`.env.example` 只提供欄位範例，可以正常提交。部署到 Render 時，不會使用本機 `.env`，請在服務的 **Environment** 頁面另外新增 `APP_PASSWORD`。

## API

| Method | Endpoint | 說明 |
|---|---|---|
| `GET` | `/api/health` | 健康檢查 |
| `GET` | `/api/auth` | 查詢登入狀態 |
| `POST` | `/api/login` | 登入，body: `{"password":"密碼"}` |
| `POST` | `/api/logout` | 登出 |
| `GET` | `/api/tasks` | 取得全部待辦 |
| `GET` | `/api/zodiac` | 取得星座；可用 `?q=獅子` 搜尋 |
| `POST` | `/api/ai-reading` | 依生日判斷星座並產生 Gemini 個人化解讀 |
| `GET/POST` | `/api/demo-state` | `client.py` 與已開啟網頁之間的測試操作同步 |
| `POST` | `/api/tasks` | 新增待辦，body: `{"title":"內容"}` |
| `PATCH` | `/api/tasks/:id` | 更新待辦，body: `{"completed":true}` |
| `DELETE` | `/api/tasks/:id` | 刪除待辦 |
