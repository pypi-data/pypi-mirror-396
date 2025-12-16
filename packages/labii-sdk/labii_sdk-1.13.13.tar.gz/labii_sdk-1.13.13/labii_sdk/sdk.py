""" python api functions """
import os
import glob
import time
import requests
from labii_sdk.api_client import APIObject#pylint: disable=import-error

class LabiiObject:
	""" object for labii sdk """
	api = None
	organization__sid = None
	table_file = None

	def __init__(self,
		organization__sid,
		base_url="https://www.labii.dev",
		email=None,
		password=None,
		api_key=None,
		api=None
	):
		if api is None:
			self.api = APIObject(base_url=base_url, email=email, password=password, api_key=api_key, organization__sid=organization__sid)
		else:
			self.api = api
		# accounts
		self.Profile = self.APIResource(self, "accounts", "profile")
		self.APIKey = self.APIResource(self, "accounts", "apikey")
		# organizations
		self.Organization = self.APIResource(self, "organizations", "organization")
		self.People = self.APIResource(self, "organizations", "personnel")
		self.Team = self.APIResource(self, "organizations", "team")
		self.OrganizationWidget = self.APIResource(self, "organizations", "organizationwidget")
		self.SAML = self.APIResource(self, "organizations", "saml")
		self.Backup = self.APIResource(self, "organizations", "backup")
		self.Certification = self.APIResource(self, "organizations", "certification")
		self.Invoice = self.APIResource(self, "organizations", "invoice")
		self.Subscription = self.APIResource(self, "organizations", "subscription")
		self.Credit = self.APIResource(self, "organizations", "credit")
		self.Seat = self.APIResource(self, "organizations", "seat")
		self.Provider = self.APIResource(self, "organizations", "provider")
		# projects
		self.Project = self.APIResource(self, "projects", "project")
		self.Member = self.APIResource(self, "projects", "member")
		# applications
		self.Application = self.APIResource(self, "applications", "application")
		# tables
		self.Table = self.APIResource(self, "tables", "table")
		self.Column = self.APIResource(self, "tables", "column")
		self.Section = self.APIResource(self, "tables", "section")
		self.Filter = self.APIResource(self, "tables", "filter")
		self.Record = self.APIResource(self, "tables", "row")
		self.Cell = self.APIResource(self, "tables", "cell")
		self.Signer = self.APIResource(self, "tables", "signer")
		self.Version = self.APIResource(self, "tables", "version")
		self.Visitor = self.APIResource(self, "tables", "visitor")
		self.Activity = self.APIResource(self, "tables", "activity")
		self.Permission = self.APIResource(self, "tables", "permission")
		# widget
		self.Widget = self.APIResource(self, "widgets", "widget")
		# workflow
		self.Workflow = self.APIResource(self, "workflows", "workflow")
		# dashboard
		self.Dashboard = self.APIResource(self, "dashboard", "dashboard")
		# notification
		self.Notification = self.APIResource(self, "notifications", "notification")
		# support
		self.Video = self.APIResource(self, "support", "video")
		self.Ticket = self.APIResource(self, "support", "ticket")
		# AI
		self.GPT = self.APIResource(self, "support", "gpt")
		self.Conversation = self.APIResource(self, "support", "conversation")
		self.Question = self.APIResource(self, "support", "question")

	def switch_organization(self, organization__sid):
		""" switch organization """
		self.organization__sid = organization__sid
		self.api.organization__sid = organization__sid

	def get_columns(self, query):
		""" return object with column name as key and sid as value """
		columns = {}
		for column in self.Column.list(query=query, serializer="name", all_pages=True)["results"]:
			columns[column["name"]] = column["sid"]
		return columns

	def get_file_table(self):
		""" download the file table """
		response = self.Table.list(query="name_system=file", serializer="detail")
		self.table_file = response["results"][0]

	def upload(self, file_path, projects):
		"""
			Upload a file for files table
			Based on files/FileUpload.js
			Args:
				- file_path, the full file path
				- projects, list of projects in the format of [{"sid": "project__sid"}]
		"""
		file_name = os.path.basename(file_path)
		print(f"Uploading {file_name}...")
		# get file table
		if self.table_file is None:
			self.get_file_table()
		# create file record
		data = {
			"projects": projects,
			"name": file_name
		}
		file_size = os.path.getsize(file_path)
		column_path_sid = ""
		column_size_sid = "" #pylint: disable=unused-variable
		for column in self.table_file["columns"]:
			# file size
			if column["widget"]["sid"] == "KNQT0a40x5fMRW27bgl":
				data[column["sid"]] = file_size
				column_size_sid = column["sid"]
			# file path
			if column["widget"]["sid"] == "JMPS0a40x5eLQV16afk":
				data[column["sid"]] = file_name
				column_path_sid = column["sid"]
		file_record = self.Record.create(
			data,
			query=f"table__sid={self.table_file['sid']}&presigned_post=true"
		)
		# upload the file
		data = file_record["presigned_post"]["fields"]
		file_ob = open(file_path, 'rb') # pylint: disable=consider-using-with
		if "amazonaws.com" in file_record["presigned_post"]["url"]:
			response = requests.post(
				url=file_record["presigned_post"]["url"],
				data=data,
				files={'file': file_ob}
			)
			# update version id
			if "x-amz-version-id" in response.headers:
				data = {}
				data[column_path_sid] = f"{file_record['presigned_post']['fields']['key'].split('?')[0]}?versionId={response.headers['x-amz-version-id']}"
				response = self.Record.modify(
					file_record["sid"],
					data
				)
				return response
		elif "/row/upload/" in file_record["presigned_post"]["url"]:
			headers = self.api.get_headers(True)
			headers["Content-Type"] = "multipart/form-data"
			response = requests.post(
				url=file_record["presigned_post"]["url"],
				data=data,
				files={'file': file_ob},
				headers=headers
			)
			return file_record
		return None

		def watch_folder(self, folder_path, projects, interval=5):#pylint: disable=unreachable,unused-variable
			"""
				watch the a folder and upload files if found
				files will be uploaded to the files table
				after file is uploaded, it will be moved to a subfolder "uploaded"
				Args:
					- folder_path, the folder or path to search
					- projects, list of projects in the format of [{"sid": "project__sid"}]
					- interval, how often to check
			"""
			# check if exists
			if not os.path.exists(folder_path):
				raise RuntimeError(f"Error: folder ({folder_path}) does not exists!")
			# add "/" to path
			folder_path = folder_path.rstrip("/")
			# create a uploaded folder
			if not os.path.isdir(f"{folder_path}/uploaded/"):
				os.system(f"mkdir -p {folder_path}/uploaded/")
			# start watching
			print(f"Start watching folder ({folder_path})...")
			while True:
				time.sleep(interval)
				files = glob.glob(f'{folder_path}/*')
				for file_path in files:
					if not "/uploaded" in file_path:
						# check token in case expired
						self.api.check_token()
						# upload the file
						print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Uploading {file_path.replace(folder_path, '')}...", end="")
						self.upload(file_path, projects)
						# move the file
						os.system(f"mv {file_path} {folder_path}/uploaded/")
						print("SUCCESS")

	class APIResource:
		""" abstract class """
		app = None
		model = None

		class Meta:
			""" meta """
			abstract = True

		def __init__(self, instance, app, model):
			"""
				- instance, the outer instance
			"""
			self.instance = instance
			self.app = app
			self.model = model

		def create(self, data, query=""):
			"""
				Create a object
				Args:
				- data (dict), the object data
			"""
			return self.instance.api.post(
				self.instance.api.get_list_url(self.app, self.model, serializer="detail", query=query),
				data
			)

		def retrieve(self, sid, query=""):
			""" Return an object """
			return self.instance.api.get(self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query))

		def list(self, page=1, page_size=10, all_pages=False, level="organization", serializer="list", query=""):
			""" Return list of objects """
			if all_pages is True:
				url = self.instance.api.get_list_url(
					self.app,
					self.model,
					sid=self.instance.api.organization__sid,
					level=level,
					serializer=serializer,
					query=query
				)
				return self.instance.api.get(url, True)
			# not all pages
			url = self.instance.api.get_list_url(
				self.app,
				self.model,
				sid=self.instance.api.organization__sid,
				level=level,
				serializer=serializer,
				query=f"page={page}&page_size={page_size}{'' if query == '' else '&'}{query}"
			)
			return self.instance.api.get(url)

		def modify(self, sid, data, query=""):
			"""
				Change one object
				Args:
				- data (dict), the object data
			"""
			return self.instance.api.patch(
				self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query),
				data
			)

		def delete(self, sid, query=""):
			""" Delete a object """
			return self.instance.api.delete(self.instance.api.get_detail_url(self.app, self.model, sid=sid, query=query))
