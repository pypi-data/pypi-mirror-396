import os, re, apsw
import markdown2, re
from nicegui import ui, app
from biblemategui import get_translation
from biblemategui import BIBLEMATEGUI_DATA
from biblemategui.fx.bible import BibleSelector
from functools import partial
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
# auth-related imports
from biblemategui.fx.cloud_index_manager import get_drive_service, CloudIndexManager
import json
import io
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 2. OAUTH SETUP ---
app.add_middleware(SessionMiddleware, secret_key=config.storage_secret)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=config.google_client_id,
    client_secret=config.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/drive.appdata openid email profile',
        'prompt': 'consent',      # <--- FORCE new refresh token
    }, 
    # This is critical for the error you saw:
    authorize_params={'access_type': 'offline'}
)

class CloudNotepad:
    def __init__(self, content=""):
        self.text_content = content
        self.is_editing = True
        self.parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        
    def setup_ui(self):

        # --- Content Area ---
        # Card must be 'flex flex-col' so the child (textarea) can grow
        with ui.card().classes('w-full h-[75vh] p-0 flex flex-col'):
            
            # 1. Edit Mode: Text Area
            # We apply our custom 'full-height-textarea' class here
            self.textarea = ui.textarea(
                placeholder='Start typing your notes here...',
                value=self.text_content
            ).classes('w-full flex-grow full-height-textarea p-2 border-none focus:outline-none') \
             .props('flat squares resize-none') \
             .bind_visibility_from(self, 'is_editing')

            # 2. Read Mode: HTML Preview
            with ui.scroll_area().classes('w-full flex-grow p-2') \
                    .bind_visibility_from(self, 'is_editing', backward=lambda x: not x):
                self.html_view = ui.html(f'<div class="content-text">{self.text_content}</div>', sanitize=False).classes('w-full prose max-w-none')

    def toggle_mode(self):
        self.is_editing = not self.is_editing
        if not self.is_editing:
            self.update_preview()

    def update_preview(self):
        content = self.textarea.value or ''
        try:
            # Added your requested extras
            html_content = markdown2.markdown(
                content, 
                extras=["tables", "fenced-code-blocks", "toc", "cuddled-lists"]
            )
            html_content = self.parser.parseText(html_content)
            html_content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', html_content)
            html_content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", html_content)
            self.html_view.content = html_content
        except Exception as e:
            self.html_view.content = f"<p class='text-red-500'>Error: {str(e)}</p>"

    def download_file(self):
        content = self.textarea.value or ''
        if not content:
            ui.notify('Nothing to download!', type='warning')
            return
        ui.download(content.encode('utf-8'), 'biblemate_notes.md')
        ui.notify('Downloaded!', type='positive')
    
    async def handle_upload(self, e):
        try:
            content = await e.file.read()
            self.textarea.value = content.decode('utf-8')
            if not self.is_editing: self.update_preview()
            ui.notify('Loaded!', type='positive')
            self.upload.reset()
        except Exception as ex:
            ui.notify(f'Error: {str(ex)}', type='negative')
    
    def clear_text(self):
        self.textarea.value = ''
        self.html_view.content = ''
        ui.notify('Cleared!', type='info')

def notes(gui=None, b=1, c=1, v=1, area=2, **_):

    # 1. Auth Check
    token = app.storage.user.get('google_token')
    if not token:
        with ui.card().classes('absolute-center'):
            ui.html('Sign in with Google to securely save and sync your personal Bible notes across all your devices.<br><i><b>Data Policy Note:</b> BibleMate AI does not collect or store your personal notes. Your notes are saved directly within your own Google Account.</i>', sanitize=False)
            ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
            with ui.expansion(get_translation("BibleMate AI Data Policy & Privacy Commitment"), icon='privacy_tip').props('header-class="text-secondary"'):
                ui.html("<b>We respect your privacy.</b> BibleMate AI is designed to protect your personal data. We do not collect, store, or share your personal Bible notes. When you log in with your Google Account, your notes are created and stored exclusively on <b>your personal Google Drive/Account</b>, ensuring that you retain full control and ownership of your private data at all times.", sanitize=False)
        return

    service = get_drive_service(token)
    index_mgr = CloudIndexManager(service)
    notepad = CloudNotepad()

    def get_filename(verse_id):
        return f"{verse_id}.json"

    def get_vid(): 
        return f"{b}_{c}_{v}"

    def load_current_note():
        vid = get_vid()
        try:
            filename = get_filename(vid)
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])
            
            if files:
                request = service.files().get_media(fileId=files[0]['id'])
                data = json.loads(request.execute())
                return data.get("content", "")
            return ""
        except Exception as e:
            ui.notify(f"Error loading: {e}", type='negative')
            return ""

    def save_current_note():
        vid = get_vid()
        content = notepad.textarea.value
        try:
            filename = get_filename(vid)
            file_data = {"verse_id": vid, "content": content}
            media = MediaIoBaseUpload(io.BytesIO(json.dumps(file_data).encode('utf-8')), mimetype='application/json')
            
            # Find existing
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                service.files().update(fileId=files[0]['id'], media_body=media).execute()
            else:
                meta = {'name': filename, 'parents': ['appDataFolder']}
                service.files().create(body=meta, media_body=media).execute()

            # Update Index
            index_mgr.add_verse(vid)
            app.storage.user['cached_index'] = index_mgr.data
            
            ui.notify('Saved!')
            refresh_ui()
        except Exception as e:
            ui.notify(f"Error saving: {e}", type='negative')

    def delete_current_note():
        vid = get_vid()
        try:
            filename = get_filename(vid)
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                service.files().delete(fileId=files[0]['id']).execute()
                index_mgr.remove_verse(vid)
                app.storage.user['cached_index'] = index_mgr.data
                notepad.textarea.value = ""
                ui.notify('Note deleted.')
                refresh_ui()
            else:
                ui.notify('Nothing to delete.')
        except Exception as e:
            ui.notify(f"Delete error: {e}", type='negative')

    # Bible Selection menu
    bible_selector = BibleSelector(version_options=["KJV"])
    def additional_items():
        nonlocal gui, bible_selector, area
        with ui.button(icon='more_vert').props(f'flat round color={"white" if app.storage.user["dark_mode"] else "black"}'):
            with ui.menu():
                ui.menu_item(f'👁️ {get_translation("Read")} / {get_translation("Edit")}', on_click=notepad.toggle_mode)
                ui.separator()
                ui.menu_item(f'💾 {get_translation("Save")}', on_click=save_current_note)
                ui.menu_item(f'📥 {get_translation("Download")}', on_click=notepad.download_file)
                ui.menu_item(f'❌ {get_translation("Delete")}', on_click=lambda: ...)
                ui.separator()
                ui.menu_item(f'🔒 {get_translation("Logout")}', on_click=lambda: ...)
    bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False)

    notepad.setup_ui()
    notepad.textarea.value = load_current_note()

