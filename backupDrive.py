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
from passwords import mongoPass
from pymongo import MongoClient

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

def getDriveService():        
	creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
	service = build('drive', 'v3', credentials=creds)
	return service

def connectMongo():
	cluster = MongoClient(mongoPass)
	dataBased = cluster['dataBased']
	return dataBased['users']


def backupDataBased():
	print('Backing up...')
	buildDataBased()
	file_metadata = {
		'name': 'dataBased' + str(datetime.now()) + '.json',
		'mimeType': 'text/plain',
	}
	print('And...')
	media = MediaFileUpload('dataBased.json', mimetype='text/plain')
	print('Uh...')
	saveFileToDrive(file_metadata, media)
	print('Finished.')


def saveFileToDrive(file_metadata, media):
	print('Connecting to Drive...')
	service = getDriveService()
	print('Saving...')
	service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def buildDataBased():
	dataBasedBackup = {}
	dataBasedBackup['users'] = {}
	dataBased = connectMongo()
	userProfile = dataBased.find({})
	for user in userProfile:
		dataBasedBackup[user['name']] = {'flair': user['flair'], 'count': user['count'], 'pills': user['pills']}

	with open('dataBased.json', 'w') as dataBased:
		json.dump(dataBasedBackup, dataBased)