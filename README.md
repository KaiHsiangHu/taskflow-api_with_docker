# 前後端 REST API 範例

這是一個不需安裝第三方套件的待辦事項範例。後端為 Python REST API，前端為原生 HTML、CSS 與 JavaScript；資料暫存在記憶體，重新啟動後會還原。

## 啟動

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
