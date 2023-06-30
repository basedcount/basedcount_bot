from typing import Any

from googleapiclient.errors import HttpError

from backup_drive import get_drive_service


def list_files(service: Any) -> list[dict[Any, Any]]:
    results = service.files().list(pageSize=1000).execute()
    files: list[dict[Any, Any]] = results.get("files", [])
    return files


def delete_file(service: Any, file_id: str) -> None:
    try:
        service.files().delete(fileId=file_id).execute()
    except HttpError:
        print("Can't delete the file id", file_id)


# Main function
def main() -> None:
    service = get_drive_service()
    files = list_files(service)
    if not files:
        print("No files found.")
    else:
        print("Deleting files...")
        for file in files:
            delete_file(service, file["id"])
            print(f"Deleted file: {file['name']}")


if __name__ == "__main__":
    main()
