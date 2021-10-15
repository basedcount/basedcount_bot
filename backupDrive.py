from __future__ import print_function
import os.path
from datetime import timedelta, datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload
import io
from googleapiclient.http import MediaIoBaseDownload
import json
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
service = build('drive', 'v3', credentials=creds)

def backupDataBased():
	file_metadata = {
		'name': 'dataBased_test' + str(datetime.now()),
		'mimeType': 'text/plain',
	}
	media = MediaFileUpload('dataBased.json', mimetype='text/plain')
	service.files().create(body=file_metadata, media_body=media, fields='id').execute()