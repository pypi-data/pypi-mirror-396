""" test function for labii.py """
import unittest
import sys
import warnings
import boto3
from labii import LabiiObject
ssm = boto3.client('ssm', region_name='us-east-1')
labii = LabiiObject(
    "psvy0a40x18c0rwBGLQV1",
    base_url="http://127.0.0.1:8000",
    email="test@labii.com",
    password=ssm.get_parameter(Name='/labii-local/TEST/PASSWORD', WithDecryption=True)["Parameter"]["Value"]
)
labii.api.login()

class TestLabiiObject(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=ResourceWarning)
        # self.experiment__sid = "9beh0a40x1833afkpuzEJ" # the table of experiment

    def test_organization(self):
        data = labii.Organization.retrieve("psvy0a40x18c0rwBGLQV1")
        self.assertEqual(data["name"], "Test Administrator")
        # delete
        with self.assertRaises(RuntimeError, msg='{"detail":"Method \"DELETE\" not allowed."}'):
            labii.Organization.delete("psvy0a40x18c0rwBGLQV1")
    #
    # def test_get_detail_url(self):
    #     # test without query
    #     url = labii.get_detail_url("organizations", "personnel", "psvy0a40x18c0rwBGLQV1")
    #     self.assertEqual(url, f"{labii.base_url}/organizations/personnel/detail/psvy0a40x18c0rwBGLQV1/")
    #     # test with query
    #     url = labii.get_detail_url("organizations", "personnel", "psvy0a40x18c0rwBGLQV1", query="test=true")
    #     self.assertEqual(url, f"{labii.base_url}/organizations/personnel/detail/psvy0a40x18c0rwBGLQV1/?test=true")
    #
    # def test_get_headers(self):
    #     # test without token
    #     headers = labii.get_headers(is_authorized=False)
    #     self.assertTrue("X-Forwarded-For" in headers)
    #     self.assertTrue("Content-Type" in headers)
    #     self.assertTrue(headers["Content-Type"] == "application/json")
    #     self.assertFalse("Authorization" in headers)
    #     # test with token
    #     labii.token = "abcd"
    #     headers = labii.get_headers()
    #     self.assertTrue("Authorization" in headers)
    #     self.assertTrue(headers["Authorization"] == "Token abcd")

    # def test_login(self):
    #     # check successful
    #     labii.login()
    #     self.assertFalse(labii.token is None)
    #     # check wrong value
    #     with self.assertRaises(RuntimeError, msg="{'detail': 'Error: Unable to log in with provided credentials. We have notified the account (test@labii.com) about this failed attempt!'}"):
    #         labii.login(email="test@labii.com", password="xxx")

    # def test_check_token(self):
    #     # check successful
    #     labii.check_token()
    #     self.assertFalse(labii.token is None)
