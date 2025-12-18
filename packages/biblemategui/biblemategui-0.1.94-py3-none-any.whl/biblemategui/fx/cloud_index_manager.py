from biblemategui import config
import os
import json
import io
from nicegui import app, ui
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def get_drive_service(user_token):
    """Builds the Drive service with full refresh capabilities."""
    if not user_token: return None
    
    # We manually reconstruct the Credentials object with ALL details
    # so Google can refresh the token automatically when it expires.
    creds = Credentials(
        token=user_token.get('access_token'),
        refresh_token=user_token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=config.google_client_id,
        client_secret=config.google_client_secret,
        scopes=['https://www.googleapis.com/auth/drive.appdata']
    )
    return build('drive', 'v3', credentials=creds)

class CloudIndexManager:
    def __init__(self, drive_service):
        self.service = drive_service
        self.filename = 'bible_index.json'
        self.data = {} 
        self.file_id = None 

    def load_from_drive(self):
        """Downloads the index file once at startup."""
        if not self.service: return {}
        try:
            results = self.service.files().list(
                q=f"name='{self.filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                self.file_id = files[0]['id']
                request = self.service.files().get_media(fileId=self.file_id)
                content = request.execute()
                self.data = json.loads(content)
            else:
                self.data = {}
                self.save_to_drive() # Create initial file
        except Exception as e:
            print(f"Index Load Error: {e}")
        return self.data

    def save_to_drive(self):
        """Syncs the current index back to Google Drive."""
        if not self.service: return
        content = json.dumps(self.data)
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='application/json')
        file_metadata = {'name': self.filename, 'parents': ['appDataFolder']}

        try:
            if self.file_id:
                self.service.files().update(fileId=self.file_id, media_body=media).execute()
            else:
                file = self.service.files().create(body=file_metadata, media_body=media).execute()
                self.file_id = file.get('id')
        except Exception as e:
            print(f"Index Save Error: {e}")

    def add_verse(self, verse_id):
        if verse_id not in self.data:
            self.data[verse_id] = True
            self.save_to_drive()

    def remove_verse(self, verse_id):
        if verse_id in self.data:
            del self.data[verse_id]
            self.save_to_drive()

    def get_chapter_notes(self, book, chapter):
        prefix = f"{book}_{chapter}_"
        return [k for k in self.data.keys() if k.startswith(prefix)]

    def get_chapter_count(self, book, chapter):
        return len(self.get_chapter_notes(book, chapter))