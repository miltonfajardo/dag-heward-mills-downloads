import requests
import os
import re

session = requests.session()

home_folder_url = "https://www.mediafire.com/api/1.5/folder/get_content.php"


def get_song_folder_contents(url, content_type, folder_key, session=session):
    data = {
        "content_type": content_type,
        "folder_key": folder_key,
        "response_format": "json"
    }

    r = session.post(url, data=data).json()
    folder_content = r.get("response").get("folder_content")
    folders = folder_content.get("folders", [])
    files = folder_content.get("files", [])
    
    contents = {
        "folders": [],
        "files": []
    }

    for folder in folders:
        if folder["privacy"] == "public":
            contents["folders"].append({
                "name": folder["name"],
                "folderkey": folder["folderkey"],
            })

    for file in files:
        if file["privacy"] == "public" and file["password_protected"] == "no":
            contents["files"].append({
                "filename": file["filename"],
                "download_location": file["links"]["normal_download"]
            })

    return contents


def make_folders(folder_dict):
    for index, content in enumerate(folder_dict["folders"], 1):
        folder_name = content["name"]

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            print("%s. %s created" % (index, folder_name))
        else:
            print("%s. %s already exists" % (index, folder_name))


def download_content(folder_dict, session=session, write_mode="wb", dir="songs"):
    for content in folder_dict["files"]:
        filename = content["filename"]
        filename = re.sub(r'^\d+|^\d+\.', "", filename).strip()

        download_url = content["download_location"]
        filepath = os.path.join(dir, filename)

        if not os.path.exists(dir):
            os.makedirs(dir)

        file_location = session.get(download_url).text
        download_url = re.findall(r'class="DownloadButtonAd-startDownload gbtnSecondary" href=\'(.*?)\'  onclick="', file_location)

        if len(download_url) > 0:
            download_url = download_url[0]
            file_content = session.get(download_url).content
            
            with open(filepath, write_mode) as f:
                f.write(file_content)

            print("%s downloaded" % (filename))


folders = get_song_folder_contents(home_folder_url, "folders", "3xf1hfxxuhj6f")
files = get_song_folder_contents(home_folder_url, "files", "3xf1hfxxuhj6f")

for folder in folders["folders"]:
    content_dict = get_song_folder_contents(home_folder_url, "files", folder["folderkey"])
    download_content(content_dict)


print("COMPLETE")
