import os
import io
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import json

# === CONFIG ===
SERVICE_ACCOUNT_PATH = 'gcp-key.json'
FOLDER_ID = '1U7OG43L2CxsB3rdrGXHFwA8e_xWLb3IcYlrFaZhhVEmuEyu0u7_Ic-wMHEyquc83bGE1B2Eb'
GITHUB_REPO_PATH = '.'
TARGET_FOLDER = os.path.join(GITHUB_REPO_PATH, 'images')

# === SETUP GOOGLE DRIVE API ===
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_PATH, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)

# === DOWNLOAD FILES ===
def download_images():
    os.makedirs(TARGET_FOLDER, exist_ok=True)

    # Get list of image files in the Drive folder
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'image/' and trashed=false",
        fields="files(id, name)").execute()
    items = results.get('files', [])

    for item in items:
        file_id = item['id']
        file_name = item['name']
        file_path = os.path.join(TARGET_FOLDER, file_name)

        if os.path.exists(file_path):
            print(f"Skipping existing file: {file_name}")
            continue

        print(f"Downloading: {file_name}")
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

# === GIT COMMIT & PUSH ===
def git_commit_and_push():
    os.chdir(GITHUB_REPO_PATH)

    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Sync images from Google Drive'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("Changes pushed to GitHub.")

def generate_image_index(image_dir, output_path):
    images = [
        f for f in os.listdir(image_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    print(f"Found images: {images}")
    with open(output_path, 'w') as f:
        json.dump(images, f)
    print(f"Written {output_path}")

# === MAIN ===
if __name__ == '__main__':
    download_images()
    generate_image_index('images', 'images.json')
    #git_commit_and_push()
