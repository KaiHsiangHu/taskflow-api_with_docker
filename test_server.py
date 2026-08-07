import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import server


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.ApiHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.httpd.server_port

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        server.STORE = server.TaskStore()
        server.SESSIONS.clear()
        self.cookie = None

    def request(self, method, path, body=None):
        connection = HTTPConnection("127.0.0.1", self.port)
        encoded = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
        if self.cookie:
            headers["Cookie"] = self.cookie
        connection.request(method, path, encoded, headers)
        response = connection.getresponse()
        data = response.read()
        set_cookie = response.getheader("Set-Cookie")
        if set_cookie:
            self.cookie = set_cookie.split(";", 1)[0]
        connection.close()
        return response.status, json.loads(data) if data else None

    def login(self, password=None):
        return self.request(
            "POST",
            "/api/login",
            {"password": password or server.APP_PASSWORD},
        )

    def test_task_crud(self):
        status, auth = self.login()
        self.assertEqual(status, 200)
        self.assertTrue(auth["authenticated"])

        status, tasks = self.request("GET", "/api/tasks")
        self.assertEqual(status, 200)
        self.assertEqual(len(tasks), 2)

        status, task = self.request("POST", "/api/tasks", {"title": "測試 API"})
        self.assertEqual(status, 201)
        self.assertEqual(task["title"], "測試 API")

        status, task = self.request("PATCH", f"/api/tasks/{task['id']}", {"completed": True})
        self.assertEqual(status, 200)
        self.assertTrue(task["completed"])

        status, _ = self.request("DELETE", f"/api/tasks/{task['id']}")
        self.assertEqual(status, 204)

    def test_validation(self):
        self.login()
        status, error = self.request("POST", "/api/tasks", {"title": "  "})
        self.assertEqual(status, 400)
        self.assertIn("error", error)

    def test_authentication_required(self):
        status, error = self.request("GET", "/api/tasks")
        self.assertEqual(status, 401)
        self.assertEqual(error["error"], "請先登入")

        status, error = self.login("wrong-password")
        self.assertEqual(status, 401)
        self.assertEqual(error["error"], "密碼錯誤")

    def test_logout(self):
        self.login()
        status, _ = self.request("POST", "/api/logout", {})
        self.assertEqual(status, 200)
        status, _ = self.request("GET", "/api/tasks")
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
