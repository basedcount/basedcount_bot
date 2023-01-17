from datetime import datetime
from pathlib import Path
from typing import Any

import ujson
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.metadata"]


def get_drive_service() -> Any:
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    return service


def backup_databased(data_based: list[dict[str, object]]) -> None:
    print("Downloading data...", flush=True)
    build_data_based(data_based)
    file_metadata = {
        "name": f"dataBased{datetime.now()}.json",
        "mimeType": "application/json",
    }
    print("Preparing File...", flush=True)
    media = MediaFileUpload("dataBased.json", mimetype="application/json", resumable=True)
    save_file_to_drive(file_metadata, media)
    Path("dataBased.json").unlink(missing_ok=True)
    print("Finished", flush=True)


def save_file_to_drive(file_metadata: dict[str, str], media: MediaFileUpload) -> None:
    print("Connecting to Drive...", flush=True)
    service = get_drive_service()
    print("Uploading to Google Drive...", flush=True)
    db_file = service.files().create(body=file_metadata, media_body=media, fields="id")
    media.stream()

    response = None
    while response is None:
        status, response = db_file.next_chunk()
        if status:
            print(f"Uploaded {status.progress() * 100}", flush=True)


def build_data_based(data_based: list[dict[str, object]]) -> None:
    for user in data_based:
        del user["_id"]

    with open("dataBased.json", "w") as fp:
        ujson.dump(data_based, fp, indent=4)
