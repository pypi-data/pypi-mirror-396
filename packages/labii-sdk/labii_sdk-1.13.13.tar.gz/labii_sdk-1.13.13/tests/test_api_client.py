""" test function for labii.py """
import unittest
import sys
import warnings
import boto3
from labii_sdk.api_client import APIObject
ssm = boto3.client('ssm', region_name='us-east-1')
api = APIObject(
    base_url="http://127.0.0.1:8000",
    email="test@labii.com",
    password=ssm.get_parameter(Name='/labii-local/TEST/PASSWORD', WithDecryption=True)["Parameter"]["Value"],
    organization__sid="psvy0a40x18c0rwBGLQV1"
)

class TestAPIObject(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=ResourceWarning)

    def test_get_list_url(self):
        # test without query
        url = api.get_list_url("organizations", "personnel")
        self.assertEqual(url, "/organizations/personnel/list/organization/psvy0a40x18c0rwBGLQV1/list/")
        # test with query
        url = api.get_list_url("organizations", "personnel", query="test=true")
        self.assertEqual(url, "/organizations/personnel/list/organization/psvy0a40x18c0rwBGLQV1/list/?test=true")

    def test_get_detail_url(self):
        # test without query
        url = api.get_detail_url("organizations", "personnel", "psvy0a40x18c0rwBGLQV1")
        self.assertEqual(url, "/organizations/personnel/detail/psvy0a40x18c0rwBGLQV1/")
        # test with query
        url = api.get_detail_url("organizations", "personnel", "psvy0a40x18c0rwBGLQV1", query="test=true")
        self.assertEqual(url, "/organizations/personnel/detail/psvy0a40x18c0rwBGLQV1/?test=true")

    def test_get_headers(self):
        # test without token
        headers = api.get_headers(is_authorized=False)
        self.assertTrue("X-Forwarded-For" in headers)
        self.assertTrue("Content-Type" in headers)
        self.assertTrue(headers["Content-Type"] == "application/json")
        self.assertFalse("Authorization" in headers)
        # test with token
        api.token = "abcd"
        headers = api.get_headers()
        self.assertTrue("Authorization" in headers)
        self.assertTrue(headers["Authorization"] == "Token abcd")

    def test_login(self):
        # check successful
        api.login()
        self.assertFalse(api.token is None)
        # check wrong value
        with self.assertRaises(RuntimeError, msg="{'detail': 'Error: Unable to log in with provided credentials. We have notified the account (test@labii.com) about this failed attempt!'}"):
            api.login(email="test@labii.com", password="xxx")

    def test_check_token(self):
        # check successful
        api.check_token()
        self.assertFalse(api.token is None)
