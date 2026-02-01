import unittest
import json
from app import app, db, Paste


class PastebinTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_load(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Local Pastebin", response.data)

    def test_create_paste_via_form(self):
        response = self.app.post(
            "/", data=dict(content="Hello World"), follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello World", response.data)
        self.assertIn(b"Paste:", response.data)

    def test_create_paste_via_api_json(self):
        response = self.app.post(
            "/api/paste",
            data=json.dumps({"content": "API JSON Paste"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)
        self.assertIn("url", data)

        # Verify persistence
        paste_id = data["id"]
        with app.app_context():
            paste = Paste.query.filter_by(id=paste_id).first()
            self.assertIsNotNone(paste)
            self.assertEqual(paste.content, "API JSON Paste")

    def test_create_paste_via_api_text(self):
        response = self.app.post(
            "/api/paste", data="Raw Text Paste", content_type="text/plain"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)

        paste_id = data["id"]
        # Fetch via API
        get_response = self.app.get(f"/api/paste/{paste_id}")
        self.assertEqual(get_response.status_code, 200)
        get_data = json.loads(get_response.data)
        self.assertEqual(get_data["content"], "Raw Text Paste")

    def test_modify_paste(self):
        # First, create a paste
        with app.app_context():
            p = Paste(id="testedit", content="Original Content")
            db.session.add(p)
            db.session.commit()

        # Now, modify it
        response = self.app.post(
            "/modify/testedit",
            data=dict(content="Updated Content"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Updated Content", response.data)
        self.assertNotIn(b"Original Content", response.data)


if __name__ == "__main__":
    unittest.main()
