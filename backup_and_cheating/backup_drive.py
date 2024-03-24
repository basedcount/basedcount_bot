from __future__ import annotations

import bz2
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import ujson
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from utility_functions import create_logger

backup_drive_logger = create_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.metadata"]


def get_drive_service(service_account_file: str = "service_account.json") -> Any:
    # Load the service account key JSON file
    if Path(service_account_file).exists():
        creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    else:
        raise FileNotFoundError(f"Service account key file not found: {service_account_file}")

    service = build("drive", "v3", credentials=creds)
    return service


def backup_databased(data_based: list[dict[str, object]]) -> None:
    backup_drive_logger.info("Downloading data...")
    build_data_based(data_based)

    file_metadata = {"name": f"dataBased{datetime.now()}.json.bz2", "mimeType": "application/json", "parents": get_folder_ids(["BasedCountBackups"])}
    backup_drive_logger.info("Preparing File...")
    media = MediaFileUpload("dataBased.json.bz2", mimetype="application/x-bzip2", resumable=True)
    save_file_to_drive(file_metadata, media)

    Path("dataBased.json.bz2").unlink(missing_ok=True)
    backup_drive_logger.info("Finished")


def get_folder_ids(folder_names: list[str]) -> list[str]:
    service = get_drive_service()
    folder_ids = []
    for folder_name in folder_names:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="nextPageToken, files(id)").execute()
        items = results.get("files", [])
        if items:
            folder_id: str = items[0]["id"]
            folder_ids.append(folder_id)
    if not folder_ids:
        raise FileNotFoundError(f"Could not find any of the folders: {', '.join(folder_names)}")
    return folder_ids


def save_file_to_drive(file_metadata: dict[str, Sequence[str]], media: MediaFileUpload) -> None:
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

    with bz2.open("dataBased.json.bz2", "wb") as fp:
        fp.write(ujson.dumps(data_based, indent=4).encode("utf-8"))
