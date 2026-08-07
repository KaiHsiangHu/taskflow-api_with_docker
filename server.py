"""A dependency-free REST API and static file server for a small task app."""

from __future__ import annotations

import json
import os
import secrets
from http.cookies import SimpleCookie
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


load_dotenv()


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
APP_PASSWORD = os.environ.get("APP_PASSWORD", "taskflow123")

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
SESSIONS: set[str] = set()


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "TaskApi/1.0"

    def _json(
        self,
        data: object,
        status: HTTPStatus = HTTPStatus.OK,
        headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
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

    def _session_token(self) -> str | None:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        session = cookie.get("taskflow_session")
        return session.value if session else None

    def _is_authenticated(self) -> bool:
        token = self._session_token()
        return token is not None and token in SESSIONS

    def _require_auth(self) -> bool:
        if self._is_authenticated():
            return True
        self._json({"error": "請先登入"}, HTTPStatus.UNAUTHORIZED)
        return False

    def _cookie_header(self, token: str, max_age: int | None = None) -> str:
        parts = [f"taskflow_session={token}", "Path=/", "HttpOnly", "SameSite=Strict"]
        if self.headers.get("X-Forwarded-Proto") == "https":
            parts.append("Secure")
        if max_age is not None:
            parts.append(f"Max-Age={max_age}")
        return "; ".join(parts)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/tasks":
            if not self._require_auth():
                return
            self._json(STORE.list())
            return
        if path == "/api/auth":
            self._json({"authenticated": self._is_authenticated()})
            return
        if path == "/api/health":
            self._json({"status": "ok"})
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/login":
            data = self._read_json()
            password = data.get("password", "") if data else ""
            if not isinstance(password, str) or not secrets.compare_digest(password, APP_PASSWORD):
                self._json({"error": "密碼錯誤"}, HTTPStatus.UNAUTHORIZED)
                return
            token = secrets.token_urlsafe(32)
            SESSIONS.add(token)
            self._json(
                {"authenticated": True},
                headers={"Set-Cookie": self._cookie_header(token)},
            )
            return
        if path == "/api/logout":
            token = self._session_token()
            if token:
                SESSIONS.discard(token)
            self._json(
                {"authenticated": False},
                headers={"Set-Cookie": self._cookie_header("", max_age=0)},
            )
            return
        if path != "/api/tasks":
            self._json({"error": "找不到 API"}, HTTPStatus.NOT_FOUND)
            return
        if not self._require_auth():
            return
        data = self._read_json()
        title = data.get("title", "").strip() if data else ""
        if not title:
            self._json({"error": "title 為必填欄位"}, HTTPStatus.BAD_REQUEST)
            return
        self._json(STORE.create(title), HTTPStatus.CREATED)

    def do_PATCH(self) -> None:
        if not self._require_auth():
            return
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
        if not self._require_auth():
            return
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
