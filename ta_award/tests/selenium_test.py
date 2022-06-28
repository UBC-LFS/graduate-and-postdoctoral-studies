from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class SeleniumTests(TestCase):
    fixtures = [
        'ta_award/fixtures/accesslevels.json',
        'ta_award/fixtures/customuser_accesslevels.json',
        'ta_award/fixtures/customusers.json',
        'ta_award/fixtures/users.json'
    ]

    def test_login(self):
        print('test_login')