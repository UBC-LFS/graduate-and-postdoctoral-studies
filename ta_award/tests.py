from django.test import TestCase
from django.contrib.messages import get_messages

from . import api as accountApi

LOGIN_URL = '/accounts/local_login/'
ContentType='application/x-www-form-urlencoded'

DATA = [
    'ta_award/fixtures/accesslevels.json',
    'ta_award/fixtures/customuser_accesslevels.json',
    'ta_award/fixtures/customusers.json',
    'ta_award/fixtures/users.json'
]

USERS = [ 'user1.admin', 'user3.manager', 'user6.guest']
PASSWORD = 'password'

class SessionTest(TestCase):
    fixtures = DATA

    # @classmethod
    # def setUpTestData(cls):
    #     print('\nSession testing has started ==>')
    #     cls.user = accountApi.get_user_by_username(USERS[0])

    # def login(self, username=None, password=None):
    #     if username and password:
    #         self.client.post(LOGIN_URL, data={'username': username, 'password': password})
    #     else:
    #         self.client.post(LOGIN_URL, data={'username': self.user.username, 'password': PASSWORD})

    # def messages(self, res):
    #     return [m.message for m in get_messages(res.wsgi_request)]

    def test_view_url_exists_at_desired_location(self):
        print('test_view_url_exists_at_desired_location')
        # self.login(USERS[0], 'password')
        pass

    # def test_user_exists(self):
    #     print('- Test: check wheter a user exists')
    #     self.login()
