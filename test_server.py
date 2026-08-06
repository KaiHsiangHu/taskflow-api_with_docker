import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import server


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.STORE = server.TaskStore()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.ApiHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.httpd.server_port

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(self, method, path, body=None):
        connection = HTTPConnection("127.0.0.1", self.port)
        encoded = json.dumps(body).encode() if body is not None else None
        connection.request(method, path, encoded, {"Content-Type": "application/json"})
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, json.loads(data) if data else None

    def test_task_crud(self):
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
        status, error = self.request("POST", "/api/tasks", {"title": "  "})
        self.assertEqual(status, 400)
        self.assertIn("error", error)


if __name__ == "__main__":
    unittest.main()
