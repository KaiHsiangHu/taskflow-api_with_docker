"""A dependency-free REST API and static file server for a small task app."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000
STATIC_DIR = Path(__file__).with_name("frontend")


class TaskStore:
    """In-memory task storage used by the example API."""

    def __init__(self) -> None:
        self._next_id = 3
        self._tasks = [
            {"id": 1, "title": "閱讀 API 文件", "completed": True},
            {"id": 2, "title": "新增第一個待辦事項", "completed": False},
        ]

    def list(self) -> list[dict]:
        return [task.copy() for task in self._tasks]

    def create(self, title: str) -> dict:
        task = {"id": self._next_id, "title": title, "completed": False}
        self._next_id += 1
        self._tasks.append(task)
        return task.copy()

    def update(self, task_id: int, values: dict) -> dict | None:
        for task in self._tasks:
            if task["id"] == task_id:
                task.update(values)
                return task.copy()
        return None

    def delete(self, task_id: int) -> bool:
        for index, task in enumerate(self._tasks):
            if task["id"] == task_id:
                del self._tasks[index]
                return True
        return False


STORE = TaskStore()


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "TaskApi/1.0"

    def _json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            value = json.loads(self.rfile.read(length))
            return value if isinstance(value, dict) else None
        except (ValueError, json.JSONDecodeError):
            return None

    def _task_id(self, path: str) -> int | None:
        parts = path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "tasks"]:
            return None
        try:
            return int(parts[2])
        except ValueError:
            return None

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/tasks":
            self._json(STORE.list())
            return
        if path == "/api/health":
            self._json({"status": "ok"})
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/tasks":
            self._json({"error": "找不到 API"}, HTTPStatus.NOT_FOUND)
            return
        data = self._read_json()
        title = data.get("title", "").strip() if data else ""
        if not title:
            self._json({"error": "title 為必填欄位"}, HTTPStatus.BAD_REQUEST)
            return
        self._json(STORE.create(title), HTTPStatus.CREATED)

    def do_PATCH(self) -> None:
        task_id = self._task_id(urlparse(self.path).path)
        data = self._read_json()
        if task_id is None or data is None:
            self._json({"error": "請求格式錯誤"}, HTTPStatus.BAD_REQUEST)
            return
        values = {}
        if "title" in data:
            if not isinstance(data["title"], str) or not data["title"].strip():
                self._json({"error": "title 不可為空"}, HTTPStatus.BAD_REQUEST)
                return
            values["title"] = data["title"].strip()
        if "completed" in data:
            if not isinstance(data["completed"], bool):
                self._json({"error": "completed 必須是布林值"}, HTTPStatus.BAD_REQUEST)
                return
            values["completed"] = data["completed"]
        task = STORE.update(task_id, values)
        self._json(task if task else {"error": "找不到待辦事項"},
                   HTTPStatus.OK if task else HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        task_id = self._task_id(urlparse(self.path).path)
        if task_id is None:
            self._json({"error": "請求格式錯誤"}, HTTPStatus.BAD_REQUEST)
            return
        if not STORE.delete(task_id):
            self._json({"error": "找不到待辦事項"}, HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def _serve_static(self, path: str) -> None:
        files = {
            "/": "index.html",
            "/app.js": "app.js",
            "/style.css": "style.css",
            "/logo.svg": "logo.svg",
        }
        filename = files.get(path)
        if not filename:
            self._json({"error": "找不到頁面"}, HTTPStatus.NOT_FOUND)
            return
        body = (STATIC_DIR / filename).read_bytes()
        content_type = {
            ".html": "text/html",
            ".js": "text/javascript",
            ".css": "text/css",
            ".svg": "image/svg+xml",
        }[Path(filename).suffix]
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = HOST, port: int = PORT) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"Task API running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
