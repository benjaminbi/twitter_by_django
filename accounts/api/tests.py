from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.createUser(
            username='admin1',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # test must use post, get is not allowed
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 405)

        # use post with wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': "wrong password",
        })
        self.assertEqual(response.status_code, 400)

        # not logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # login in with correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': "correct password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')

        # verify is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # log in first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # verify user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test "must use post"
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # use post to logout successfully
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # verify user is logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }

        # test "get" should fail
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test with wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # test with short password
        response = self.client.post(SIGNUP_URL, {
            'name': 'someone',
            'email': 'not a correct email',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        # test with long username
        response = self.client.post(SIGNUP_URL, {
            'name': 'user name is toooooooooooooooooooooooooooooo looooooooooooooooooooooooooooooooooooog',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # test sign in with correct input
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # verify user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
