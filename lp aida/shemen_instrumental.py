import html
import os
import re
import time
from urllib import parse

import click
import requests


def get_all_songs_in_page():
    url = "https://shemenmusic.bandcamp.com"
    source = requests.get(url).text
    source = html.unescape(source)

    files = re.findall(
        r'"page_url":"(?P<url>.*?)","title":"(?P<title>.*?)"', source)
    files = [{"url": parse.urljoin(url, x[0]), "name": x[1]} for x in files]

    return files


def download_file(song_dict):
    url = song_dict.get("url")
    filename = song_dict.get("name")

    if not (url and filename):
        return

    main_folder = "shemen instrumentals"

    if not os.path.exists(main_folder):
        os.mkdir(main_folder)

    filename = filename.lower().replace("?", "-").replace("\\", "-")
    filename = "%s.mp3" % filename

    source = requests.get(url).text
    download_url = re.search(r'"file":\{"mp3-\d+":"(.*?)"\}', source)

    if download_url:
        download_url = download_url.group(1)

    file_path = "%s/%s" % (main_folder, filename)
    r = requests.get(download_url, stream=True)
    total_length = int(r.headers.get('content-length'))
    chunks = r.iter_content(chunk_size=1024)

    with click.progressbar(chunks, length=int(total_length/1024) + 1, label="Downloading %s" % filename, show_percent=True, show_pos=True, show_eta=True, width=50, color="green") as bar, open(file_path, "wb") as f:
        for chunk in bar:
            f.write(chunk)
            f.flush()

            bar.update(int(len(chunk)/2048))


if __name__ == "__main__":
    songs = get_all_songs_in_page()

    start_time = time.perf_counter()
    print("About to download %s songs\n" % len(songs))

    for song in songs:
        download_file(song)

    end_time = time.perf_counter()
    total_time = int(end_time - start_time)

    print("%s DOWNLOAD COMPLETE IN %s seconds" % (len(songs), total_time))
