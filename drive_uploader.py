import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(filename):
    creds_json = json.loads(os.environ.get("GOOGLE_CREDS_JSON"))
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": filename,
        "parents": ["root"]
    }
    media = MediaFileUpload(filename, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    file_id = uploaded.get("id")
    permission = {
        "role": "reader",
        "type": "anyone"
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    file_url = f"https://drive.google.com/file/d/{file_id}/view"
    return file_url
