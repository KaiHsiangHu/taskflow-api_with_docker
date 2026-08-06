# 前後端 REST API 範例

這是一個不需安裝第三方套件的待辦事項範例。後端為 Python REST API，前端為原生 HTML、CSS 與 JavaScript；資料暫存在記憶體，重新啟動後會還原。

## 啟動

在專案根目錄執行：

```powershell
python api_example/server.py
```

然後開啟 <http://127.0.0.1:8000>。也可以在 VS Code 的「執行與偵錯」選擇 **啟動前後端 API 範例**。

## API

| Method | Endpoint | 說明 |
|---|---|---|
| `GET` | `/api/health` | 健康檢查 |
| `GET` | `/api/tasks` | 取得全部待辦 |
| `POST` | `/api/tasks` | 新增待辦，body: `{"title":"內容"}` |
| `PATCH` | `/api/tasks/:id` | 更新待辦，body: `{"completed":true}` |
| `DELETE` | `/api/tasks/:id` | 刪除待辦 |
