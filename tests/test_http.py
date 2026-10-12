import http.cookiejar
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


class HttpFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        server.DB_PATH = os.path.join(cls.folder.name, 'integration.sqlite3')
        server.setup()
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.base = 'http://127.0.0.1:%d' % cls.httpd.server_port
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)
        cls.folder.cleanup()

    def setUp(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def get(self, endpoint):
        with self.opener.open(self.base + endpoint) as response:
            return json.load(response)

    def post(self, endpoint, body, csrf=None):
        headers = {'Content-Type': 'application/json'}
        if csrf: headers['X-CSRF-Token'] = csrf
        req = urllib.request.Request(self.base + endpoint, json.dumps(body).encode(), headers=headers, method='POST')
        with self.opener.open(req) as response:
            return json.load(response)

    def test_signup_logout_login_cycle(self):
        signed = self.post('/api/signup', {'name': 'Test User', 'email': 'example@reflect.test', 'password': 'correct-password-123'})
        self.assertEqual(signed['user']['name'], 'Test User')
        self.assertEqual(self.get('/api/me')['user']['email'], 'example@reflect.test')
        self.post('/api/logout', {}, signed['csrf'])
        self.assertIsNone(self.get('/api/me')['user'])
        logged = self.post('/api/login', {'email': 'example@reflect.test', 'password': 'correct-password-123'})
        self.assertEqual(logged['user']['name'], 'Test User')
        self.post('/api/logout', {}, logged['csrf'])
        self.assertIsNone(self.get('/api/me')['user'])

    def test_login_with_existing_password_account(self):
        # v0.1/v0.2 users have the same PBKDF2 format as v0.3.1.
        email='legacy@reflect.test'
        with server.conn() as db:
            db.execute('INSERT INTO users(name,email,passhash,created_at) VALUES(?,?,?,?)',
                       ('Legacy User',email,server.hash_password('old-password-123'),server.now()))
        result=self.post('/api/login',{'email':email,'password':'old-password-123'})
        self.assertEqual(result['user']['name'],'Legacy User')
        self.assertIsNotNone(self.get('/api/me')['user'])

    def test_logout_without_session(self):
        self.assertTrue(self.post('/api/logout', {})['ok'])

    def test_reflection_edit_delete_and_profile(self):
        import secrets
        suffix=secrets.token_hex(5)
        email=f'edit-{suffix}@reflect.test'
        signed=self.post('/api/signup',{'name':'Editor Person','email':email,'password':'initial-password-123'})
        csrf=signed['csrf']
        created=self.post('/api/reflections',{'happened_on':'2026-09-17','situation':'A scheduled team meeting had unclear ownership','response':'I clarified assignments','learning':'Confirm owners'},csrf)
        rid=created['id']
        updated=self.post('/api/reflections/update',{'id':rid,'happened_on':'2026-09-18','situation':'A different team meeting needed an explicit agenda','response':'I wrote the agenda','learning':'Prepare earlier'},csrf)
        self.assertTrue(updated['ok'])
        items=self.get('/api/reflections')['reflections']
        self.assertEqual(next(r for r in items if r['id']==rid)['happened_on'],'2026-09-18')
        profile=self.post('/api/account/profile',{'name':'Updated Editor'},csrf)
        self.assertEqual(profile['user']['name'],'Updated Editor')
        with self.assertRaises(urllib.error.HTTPError) as wrong:
            self.post('/api/account/password',{'current_password':'wrong','new_password':'new-password-123'},csrf)
        self.assertEqual(wrong.exception.code,403)
        self.post('/api/account/password',{'current_password':'initial-password-123','new_password':'new-password-123'},csrf)
        self.post('/api/logout',{},csrf)
        new_login=self.post('/api/login',{'email':email,'password':'new-password-123'})
        csrf=new_login['csrf']
        deleted=self.post('/api/reflections/delete',{'id':rid},csrf)
        self.assertTrue(deleted['ok'])
        self.assertFalse(any(r['id']==rid for r in self.get('/api/reflections')['reflections']))

    def test_oauth_config_public(self):
        self.assertIn('google', self.get('/api/auth/providers'))


if __name__ == '__main__':
    unittest.main()
