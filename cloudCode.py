import os
import tkinter as tk
from tkinter import Listbox, Text
from tkinter import filedialog
from tkinter import Listbox, Scrollbar, Text
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import dropbox
from pcloud import PyCloud
import requests

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
with open("token.txt", "r") as tok:
    TOKEN = tok.read()
dbx = dropbox.Dropbox(TOKEN) 
pcloud_token = 'pcloud username here'
password = 'pcloud password here'
access_token="pcloud access token here"
pc = PyCloud(pcloud_token, password)

class CloudUploaderApp:
   
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 SMART CLOUD SYSTEM 🌙")

        # Create a frame with a dark background
        self.frame = tk.Frame(root, bg='#333333')
        self.frame.pack()

        self.label = tk.Label(self.frame, text="📂 Select a file to upload:", bg='#333333', fg='#FFFFFF', font=("Helvetica", 12, "bold"))
        self.label.pack()

        self.select_button = tk.Button(self.frame, text="🔍 Browse", command=self.select_file, bg='#1E90FF', fg='#FFFFFF', font=("Helvetica", 10, "bold"))
        self.select_button.pack(pady=5)

        self.upload_button = tk.Button(self.frame, text="🚀 Upload", command=self.upload, bg='#32CD32', fg='#FFFFFF', font=("Helvetica", 10, "bold"))
        self.upload_button.pack(pady=10)

        self.cloud_files_label = tk.Label(self.frame, text="☁️ Cloud Files:", bg='#333333', fg='#FFFFFF', font=("Helvetica", 12, "bold"))
        self.cloud_files_label.pack()

        self.cloud_files_listbox = Listbox(self.frame, selectmode=tk.SINGLE, height=5, font=("Helvetica", 10))
        self.cloud_files_listbox.pack()

        self.download_button = tk.Button(self.frame, text="📥 Download", command=self.download, bg='#FF4500', fg='#FFFFFF', font=("Helvetica", 10, "bold"))
        self.download_button.pack(pady=10)

        self.message_label = tk.Label(self.frame, text="📄 Status:", bg='#333333', fg='#FFFFFF', font=("Helvetica", 12, "bold"))
        self.message_label.pack()

        self.message_text = Text(self.frame, height=5, width=40, font=("Helvetica", 10), bg='#1E1E1E', fg='#FFFFFF')
        self.message_text.pack()

        self.load_cloud_files()

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.message_text.delete(1.0, tk.END)  # Clear the message text
            self.message_text.insert(tk.END, f"Selected File: {self.file_path}\n")

    def upload(self):
        if not hasattr(self, 'file_path'):
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, "No file selected for upload.")
            return

        file_extension = os.path.splitext(self.file_path)[1].lower()

        supported_extensions = [
            '.jpg', '.png', '.mp3', '.mp4', '.py', '.java', '.cpp', '.cs', '.rb', '.js',
            '.html', '.css', '.php', '.swift', '.kt', '.ts', '.json', '.xml', '.yaml',
            '.sql', '.md', '.txt', '.pdf', '.ppt', '.doc', '.xls'
        ]

        if file_extension in ['.jpg', '.png']:
            self.upload_to_google_drive(self.file_path)
            self.message_text.insert(tk.END, "Image uploaded to Google Drive\n")
        elif file_extension in ['.mp3', '.mp4']:
            self.upload_to_dropbox(self.file_path)
            self.message_text.insert(tk.END, "Audio/Video uploaded to Dropbox\n")
        elif file_extension in supported_extensions:
            self.upload_to_pcloud(self.file_path)
            self.message_text.insert(tk.END, "File uploaded to pCloud\n")
        else:
            self.message_text.insert(tk.END, "Unsupported file format\n")

        self.load_cloud_files()

    def upload_to_google_drive(self, file_path):
        drive = GoogleDrive(gauth)
        gfile = drive.CreateFile({'title': os.path.basename(file_path)})
        gfile.SetContentFile(file_path)
        gfile.Upload()

    def upload_to_dropbox(self, file_path):
        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            dbx.files_upload(f.read(), '/' + file_name)

    def upload_to_pcloud(self, file_path):
        if file_path:
            pc.uploadfile(files=[file_path])

    def load_cloud_files(self):
        self.cloud_files_listbox.delete(0, tk.END)
        if hasattr(gauth, 'credentials'):
            drive = GoogleDrive(gauth)
            file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
            for file in file_list:
                self.cloud_files_listbox.insert(tk.END, "Google Drive: " + file['title'])
        try:
            dbx.files_list_folder("")
            dbx_files = dbx.files_list_folder("").entries
            for file in dbx_files:
                self.cloud_files_listbox.insert(tk.END, "Dropbox: " + file.name)
        except dropbox.exceptions.AuthError as e:
            self.message_text.insert(tk.END, "Dropbox authentication error: " + str(e) + "\n")

        try:
            pcloud_files = pc.listfolder(path="/")
            for file in pcloud_files["metadata"]["contents"]:
                self.cloud_files_listbox.insert(tk.END, "pCloud: " + file["name"])
        except Exception as e:
            self.message_text.insert(tk.END, "pCloud error: " + str(e) + "\n")

    def download(self):
        selected_index = self.cloud_files_listbox.curselection()
        if not selected_index:
            return

        selected_item = self.cloud_files_listbox.get(selected_index)
        cloud_service = selected_item.split(":")[0].strip()
        file_name = selected_item.split(":")[1].strip()

        if cloud_service == "Google Drive":
            self.download_from_google_drive(file_name)

        elif cloud_service == "Dropbox":
            self.download_from_dropbox(file_name)

        elif cloud_service == "pCloud":
            self.download_from_pcloud(file_name)
            
    def download_from_google_drive(self, file_name):
        drive = GoogleDrive(gauth)
        file_list = drive.ListFile({'q': f"title='{file_name}' and trashed=false"}).GetList()
        if file_list:
            gfile = file_list[0]
            gfile.GetContentFile(file_name)
            self.message_text.insert(tk.END, f"Downloaded from Google Drive: {file_name}\n")
        else:
            self.message_text.insert(tk.END, f"File not found on Google Drive: {file_name}\n")

    def download_from_dropbox(self, file_name):
        try:
            dbx.files_download_to_file(file_name, "/" + file_name)
            self.message_text.insert(tk.END, f"Downloaded from Dropbox: {file_name}\n")
        except dropbox.exceptions.HttpError as e:
            self.message_text.insert(tk.END, f"Error downloading from Dropbox: {str(e)}\n")
    def download_from_pcloud(self, file_name):
        try:
            pcloud_files = pc.listfolder(path="/")
            file_info = None
            for file in pcloud_files["metadata"]["contents"]:
                if file["name"] == file_name:
                    file_info = file
                    break

            if file_info:
                file_id = file_info["fileid"]
                download_url = f"https://api.pcloud.com/downloadfile?fileid={file_id}&access_token={access_token}"
                print(download_url)
                response = requests.get(download_url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    self.message_text.insert(tk.END, f"Downloaded from pCloud: {file_name}\n")
                else:
                    self.message_text.insert(tk.END, f"Failed to download from pCloud: {file_name}\n")
            else:
                self.message_text.insert(tk.END, f"File not found on pCloud: {file_name}\n")
        except Exception as e:
            self.message_text.insert(tk.END, f"Error downloading from pCloud: {str(e)}\n")

   
if __name__ == "__main__":
    root = tk.Tk()
    app = CloudUploaderApp(root)
    root.mainloop()