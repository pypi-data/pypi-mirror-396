import unittest, boto3
from api import *
ssm = boto3.client('ssm', region_name='us-east-1')

class TestLabiiAPI(unittest.TestCase):
    def setUp(self):
        self.email = ssm.get_parameter(Name='/ACCOUNT/TEST/EMAIL')["Parameter"]["Value"]
        self.password = ssm.get_parameter(Name='/ACCOUNT/TEST/PASSWORD', WithDecryption=True)["Parameter"]["Value"]
        self.organization__sid = "behk0a40x2e6dinsxCHM" # labii test account
        self.experiment__sid = "9beh0a40x1833afkpuzEJ" # the table of experiment
        self.token = labii_auth(self.email, self.password)

    def test_labii_get_headers(self):
        # test without token
        headers = labii_get_headers()
        self.assertTrue("X-Forwarded-For" in headers)
        self.assertTrue("Content-Type" in headers)
        self.assertTrue(headers["Content-Type"] == "application/json")
        self.assertFalse("Authorization" in headers)
        # test with token
        headers = labii_get_headers("abcd")
        self.assertTrue("Authorization" in headers)
        self.assertTrue(headers["Authorization"] == "Token abcd")

    def test_labii_get(self):
        data = labii_get(f"/tables/row/list/organization/{self.organization__sid}/name/?table__sid={self.experiment__sid}", self.token)
        self.assertTrue(len(data["results"]) > 0)

    def test_labii_get_all(self):
        data = labii_get_all(f"/tables/row/list/organization/{self.organization__sid}/name/?table__sid={self.experiment__sid}", self.token)
        self.assertTrue(len(data["results"]) > 0)

    def test_labii_update_cell(self):
        import time
        data = labii_get(f"/tables/row/list/organization/{self.organization__sid}/list/?table__sid={self.experiment__sid}&is_archived=false", self.token)
        row__sid = ""
        date_start__sid = ""
        date_end__sid = ""
        today = tag = time.strftime("%Y-%m-%d")
        for r in data["results"]:
            for c in r["column_set"]:
                if c["column"]["name"] == "date_start" and c["data"] != today:
                    row__sid = r["sid"]
                    date_start__sid = c["column"]["sid"]
                if c["column"]["name"] == "date_end":
                    date_end__sid = c["column"]["sid"]
                    if c["data"] == "":
                        break
        # test existing cell
        labii_update_cell(self.token, self.organization__sid, row__sid, date_start__sid, {"data": today})
        labii_update_cell(self.token, self.organization__sid, row__sid, date_end__sid, {"data": today})
        data = labii_get(f"/tables/row/detail/{row__sid}/e", self.token)
        for c in data["column_set"]:
            self.assertEqual(c["data"], today)

    def test_labii_json_list_to_tsv(self):
        # get list of experiments
        data = labii_get(f"/tables/row/list/organization/{self.organization__sid}/detail/?table__sid={self.experiment__sid}", self.token)
        tsv = labii_json_list_to_tsv(data["results"])
        self.assertEqual(len(tsv.split("\n")), 11)

    def test_labii_check_token(self):
        token = labii_check_token(self.email, self.password, self.token)
        self.assertEqual(token, self.token)
        token = labii_check_token(self.email, self.password, "aa")
        self.assertFalse(token == "aa")

if __name__ == '__main__':
    unittest.main()
