""" api related functions """
import json
import getpass
import requests

class APIObject:
	""" api object for api functions """
	base_url = "https://www.labii.dev"
	email = None
	password = None
	token = None
	api_key = None
	organization__sid = None
	user = None

	def __init__(self, base_url="https://www.labii.dev", email=None, password=None, token=None, api_key=None, organization__sid=None, user=None):
		self.base_url = base_url
		self.email = email
		self.password = password
		self.token = token
		self.api_key = api_key
		self.organization__sid = organization__sid
		self.user = user

	######
	# url
	def get_list_url(self, app, model, level="organization", sid=None, serializer='list', query=""):
		""" return the list url """
		if sid is None:
			sid = self.organization__sid
		return f"/{app}/{model}/list/{level}/{sid}/{serializer}/{'' if query == '' else '?'}{query}"

	def get_detail_url(self, app, model, sid, query=""):
		""" return the detail url """
		return f"/{app}/{model}/detail/{sid}/{'' if query == '' else '?'}{query}"

	######
	# auth
	def get_headers(self, is_authorized=True):
		"""Return necessary headers for API functions

		Returns:
			dict: header objects
		"""
		headers = {
			"X-Forwarded-For": "batch",
			"Content-Type": "application/json"
		}
		if is_authorized:
			if self.api_key is not None:
				headers["Authorization"] = f"Bearer {self.api_key}"
			elif self.token is not None:
				headers["Authorization"] = f"Token {self.token}"
		return headers

	def login(self, email="", password=""):
		"""Get authentication token based on user input
		- self.login()
			- login with saved email/password
			- get email/password if not saved
		- self.login(email=xxx, password=xxx): login with new email/password

		Args:
			email (str): email to use to login
			password (str): password to use to login
		"""
		# get email or password
		if email != "" and password != "":
			self.email = email
			self.password = password
		else:
			if self.email is None or self.password is None:
				self.email = input("Email: ")
				self.password = getpass.getpass('Password: ')
		# get token
		data = {
			"username": self.email,
			"password": self.password
		}
		response = self.post("/accounts/auth/", data, is_authorized=False)
		if "token" in response:
			self.token = response["token"]
			self.user = response
		elif "secret" in response:# two step authentication
			# use email to verify
			self.post("/accounts/mfa/code/", {"option": "email", "secret": response["secret"]}, is_authorized=False)
			code = input("MFA enabled for the account. Please check your email and provide authentication code: ")
			data = self.post("/accounts/mfa/verify/", {"code": code, "secret": response["secret"]}, is_authorized=False)
			if "token" in data:
				self.token = data["token"]
				self.user = data
			else:
				raise RuntimeError(data)
		else:
			raise RuntimeError(response)

	def check_token(self):
		"""Check if the exist token is valid. If not valid, it will genereate a new token
			Labii token expires after 30 minutes of no activity. If your program take more than 30 minutes to run. Use this function to get a new token.
		"""
		try:
			self.get("/accounts/checktoken/")
		except:
			#if data["detail"] != "Valid token.":
			self.login()

	######
	# api post
	def post(self, url, data, is_authorized=True):
		"""A function to do POST for labii api

		Args:
			url (str): API URL
			data (dict): data to POST, see API documentation (https://docs.labii.com/api/overview) for the format
			is_authorized (bool): should use the authrized token

		Returns:
			dict: created object
		"""
		response = requests.post(url=f"{self.base_url}{url}", data=json.dumps(data, separators=(',',':')), headers=self.get_headers(is_authorized))
		if response.status_code != 200 and response.status_code != 201:
			print(f"Error: {response.status_code} - {response.text}")
			return response.text
		try:
			return json.loads(response.text)
		except:
			print(response.text)
			return response.text

	def patch(self, url, data, is_authorized=True):
		"""A function to do PATCH for labii api

		Args:
			url (str): API URL
			data (dict): data to update, see API documentation (https://docs.labii.com/api/overview) for the format
			is_authorized (bool): should use the authrized token

		Returns:
			dict: return of the api
		"""
		response = requests.patch(url=f"{self.base_url}{url}", data=json.dumps(data, separators=(',',':')), headers=self.get_headers(is_authorized))
		if response.status_code != 200 and response.status_code != 201:
			print(f"Error: {response.status_code} - {response.text}")
			return response.text
		try:
			return json.loads(response.text)
		except:
			print(response.text)
			return response.text

	def get(self, url, all_pages=False, is_authorized=True):
		"""A function to do GET for labii api

		Args:
			url (str): API URL
			all (bool): should download all
			is_authorized (bool): should use the authrized token

		Returns:
			dict: result of the url
		"""
		if all_pages is False:
			response = requests.get(url=f"{self.base_url}{url}", headers=self.get_headers(is_authorized))
			if response.status_code != 200:
				print(f"Error: {response.status_code} - {response.text}")
				return response.text
			try:
				return json.loads(response.text)
			except:
				print(response.text)
				return response.text
		else:
			page = 1
			page_size = 10
			# update url
			if "page" in url or "page_size" in url:
				query = url.split("?")[1].split("&")
				query_updated = []
				for item in query:
					if not "page" in item and not "page_size" in item:
						query_updated.append(item)
				if len(query_updated) > 0:
					url = f"{url.split('?')[0]}?{'&'.join(query_updated)}"
				else:
					url = url.split("?")[0]
			if "?" in url:
				url_with_page = f"{url}&page={page}&page_size={page_size}"
			else:
				url_with_page = f"{url}?page={page}&page_size={page_size}"
			response = requests.get(url=f"{self.base_url}{url_with_page}", headers=self.get_headers(is_authorized))
			if response.status_code != 200:
				print(f"Error: {response.status_code} - {response.text}")
				return json.loads(response.text)
			data = json.loads(response.text)
			count = data["count"]
			results = data["results"]
			print(f"Total records: {count}")
			print("Downloading page 1...")
			while len(results) < count:
				page += 1
				print(f"Downloading page {page}...")
				if "?" in url:
					url_with_page = f"{url}&page={page}&page_size={page_size}"
				else:
					url_with_page = f"{url}?page={page}&page_size={page_size}"
				response = requests.get(url=f"{self.base_url}{url_with_page}", headers=self.get_headers(is_authorized))
				if response.status_code != 200:
					print(f"Error: {response.status_code} - {response.text}")
					data = json.loads(response.text)
					results = None
					break
				results = results + json.loads(response.text)["results"]
			if results is not None:
				data["results"] = results
			return data

	def delete(self, url, is_authorized=True):
		"""A function to do delete for labii api

		Args:
			url (str): API URL
			is_authorized (bool): should use the authrized token

		Returns:
			dict: result of the url
		"""
		response = requests.delete(url=f"{self.base_url}{url}", headers=self.get_headers(is_authorized))
		if response.status_code != 200 and response.status_code != 204:
			print(f"Error: {response.status_code} - {response.text}")
			return response.text
		try:
			return json.loads(response.text)
		except:
			print(response.text)
			return response.text

#
# def labii_json_list_to_tsv(results):
#     """conver the list result in json format into tsv format
#
#     Args:
#         results (array): the results from response
#
#     Returns:
#         string: tsv data
#     """
#     if len(results) > 0:
#         should_collect_title = True
#         titles = [] # collect list of titles
#         data = [] # the data of all
#         for r in results:
#             d = [] # the data of one row
#             for field in r:
#                 if field == "column_set":
#                     for f in r["column_set"]:
#                         d.append(str(f["data"]).replace("\n","").replace("\r",""))
#                         if should_collect_title:
#                             titles.append(f["column"]["name"])
#                 elif field != "section_set":
#                     d.append(str(r[field]).replace("\n","").replace("\r",""))
#                     if should_collect_title:
#                         titles.append(field)
#             if should_collect_title:
#                 data.append("\t".join(titles))
#                 should_collect_title = False
#             data.append("\t".join(d))
#         return "\n".join(data)
#     else:
#         return "";
