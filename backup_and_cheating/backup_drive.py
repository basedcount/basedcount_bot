from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import ujson
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from utility_functions import create_logger

backup_drive_logger = create_logger(__name__)

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
    backup_drive_logger.info("Downloading data...")
    build_data_based(data_based)
    file_metadata = {
        "name": f"dataBased{datetime.now()}.json",
        "mimeType": "application/json",
    }
    backup_drive_logger.info("Preparing File...")
    media = MediaFileUpload("dataBased.json", mimetype="application/json", resumable=True)
    save_file_to_drive(file_metadata, media)
    Path("dataBased.json").unlink(missing_ok=True)
    backup_drive_logger.info("Finished")


def save_file_to_drive(file_metadata: dict[str, str], media: MediaFileUpload) -> None:
    backup_drive_logger.info("Connecting to Drive...")
    service = get_drive_service()
    backup_drive_logger.info("Uploading to Google Drive...")
    db_file = service.files().create(body=file_metadata, media_body=media, fields="id")
    media.stream()

    response = None
    while response is None:
        status, response = db_file.next_chunk()
        if status:
            backup_drive_logger.info(f"Uploaded {status.progress() * 100}")


def build_data_based(data_based: list[dict[str, object]]) -> None:
    for user in data_based:
        del user["_id"]

    with open("dataBased.json", "w") as fp:
        ujson.dump(data_based, fp, indent=4)
