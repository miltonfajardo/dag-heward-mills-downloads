import asyncio
import functools
import json
import math
import os
import re
import time
from urllib.request import urljoin

import click
import requests
import tqdm

ts = time.time()
loop = asyncio.get_event_loop()
AUDIO_URL = "http://daghewardmillsaudio1.org/index.php"


def _(text):
    TEXT = re.sub(r"[\?!_\\\/]|\s{2,}", " ", text)
    TEXT = TEXT.replace("&amp;", "&").replace("&#39;", "'").lower()
    return TEXT.strip()


def get_album_ids(id=2, limit=1000, limitstart=0, task="artist_albums", option="com_muscol"):
    params = {
        "option": option,
        "task": task,
        "id": id,
        "limitstart": limitstart,
        "limit": limit
    }

    source = requests.get(AUDIO_URL, params=params).text

    return re.findall('"id":"([\w\.\s]+)"', source)


def get_album_messages(album_id):
    params = {
        "option": "com_muscol",
        "task": "get_album_songs",
        "id": album_id,
    }

    files = requests.get(AUDIO_URL, params=params).json()

    messages_info = []

    for file in files:
        id = _(file.get("id", ""))
        artist_name = _(file.get("artist_name", "unknown"))
        album_name = _(file.get("album_name", ""))
        filename = _(file.get("name", "untitled"))

        download_url = urljoin(AUDIO_URL, file.get("file"))

        messages_info.append({
            "id": id,
            "artist_name": artist_name,
            "album_name": album_name,
            "filename": filename,
            "download_url": download_url
        })

    return messages_info


def download_message(song_dict):
    download_url = song_dict.get("download_url")
    artist_name = song_dict.get("artist_name")
    album_name = song_dict.get("album_name")
    id = song_dict.get("id")
    filename = song_dict.get("filename")

    filename = filename.split(".mp3", 1)
    filename = "{} - {}".format(filename[0], id)

    if not filename.endswith(".mp3"):
        filename = filename + ".mp3"

    if not os.path.exists(album_name):
        os.makedirs(album_name, exist_ok=True)

    filepath = "{}/{}".format(album_name, filename)

    r = requests.get(download_url, stream=True)

    total_length = int(r.headers.get('content-length', 0))
    block_size = 1024
    chunks = r.iter_content(chunk_size=block_size)

    with open(filepath, 'wb') as f:
        for data in tqdm.tqdm(chunks, total=math.ceil(total_length//block_size), unit='KB', unit_scale=True):
            f.write(data)
            f.flush()

    # with click.progressbar(chunks, length=int(total_length/1024) + 1, label="Downloading %s" % filename, show_percent=True, show_pos=True, show_eta=True, width=50, color="green") as bar, open(filepath, "wb") as f:
    #     for chunk in bar:
    #         f.write(chunk)
    #         f.flush()
            # bar.update(int(len(chunk)/2048))

    # with open(filepath, "wb") as f:
    #     content = requests.get(download_url).content

    #     f.write(content)
    #     f.flush()
    print("{} downloaded ...".format(filename))


@asyncio.coroutine
def async_download(info_dict):
    futures = []

    for info in info_dict:
        futures.append(loop.run_in_executor(
            None, functools.partial(download_message, info)))

    for req in asyncio.as_completed(futures):
        yield from req


for id in range(1, 100):
    try:
        messages = get_album_messages(id)
        print("{} => {} messages available for download ...".format(id, len(messages)))
        if len(messages) > 0:
            album_name = messages[0].get("album_name")
            print("""{}. {}\n{}\n""".format(id, album_name.upper(),
                                            "=" * (len(str(id)) + 2) +
                                            "=" * len(album_name)
                                            ))

            for message in messages:
                download_message(message)
    except Exception as err:
        print("ID: {} => {}".format(id, err))

# limit=1000, id=29

# LIMIT = 1000
# ID = 29 #2
# TASK = "get_album_songs"
# OPTION="com_muscol"

# message_ids = [int(x) for x in get_album_ids(limit=LIMIT, id=ID, task=TASK, option=OPTION)]
# message_ids = sorted(set(message_ids))
# messages = []

# for id in message_ids:
#     messages += get_album_messages(id)
#     print(".", end="", flush=True)

# print()

# with open("../errorlog.txt", "a") as f:
#     for message in messages:
#         filename = message.get("filename")
#         album_name = message.get("album_name")
#         try:
#             download_message(message)
#         except Exception as err:
#             print(err, "Can't download", filename)
#             f.write("{} <= {}".format(filename, album_name))

# # loop.run_until_complete(async_download(messages))
te = time.time()
print("Completed in: %.2s seconds" % str(te - ts))
