import os
import re
import sys
from urllib.parse import urljoin
from urllib.request import urlopen
import json

	
def get_album_id(url):
    r = urlopen(url).read().decode("utf-8")
    album_id = re.search(r'album-id="(\w+)"', r)

    if album_id:
        return album_id.group(1)
    else:
        album_id = re.findall(r'(\d+)', url)[-1]
        return album_id

def get_album_data(album_id):
    url = album_info_url.format(album_id)
    data = urlopen(url).read().decode("utf-8")
    data = json.loads(data)

    return data


album_info_url = "http://daghewardmillsaudio.org/index.php?option=com_muscol&task=get_album_songs&id={0}"
links = []

if len(sys.argv) == 1:
	if not os.path.isfile("links.txt"):
		with open("links.txt", "w") as f:
			f.write("# Please provide links that starts with 'http'. Anything else will be ignored\n")
			
		print("links.txt file does not exist but has been created.") 
		print("Please provide all your download links there line by line")
		print()
		
	with open("links.txt") as f:
		links = filter(lambda x: x.strip().startswith(
			"http"), f.read().split("\n"))
		links = list(set(links))
elif len(sys.argv) > 1:
	links = [sys.argv[1]]


if len(links) == 0:
	print("no valid url found")
	
else:	
	for link in links:
		album_id = get_album_id(link)
		album_data = get_album_data(album_id)

		if len(album_data) > 0:
			print("From: %s" % album_data[0].get("artist_name", "..."))

			album_name = album_data[0].get("album_name", "__")
			album_name = album_name.lower().strip()

			print("'%s' media available in album: '%s'\n" %
				  (len(album_data), album_name))

			if not os.path.exists(album_name):
				os.makedirs(album_name)

			dir_contents = os.listdir(album_name)

			for i in album_data:
				download_url = urljoin(album_info_url, i.get("download_link", ""))
				filename = i.get("filename", i.get("name"))

				if filename not in dir_contents:
					print("downloading '%s'" % filename, end=" ... ", flush=True)
					with open("%s/%s" % (album_name, filename), "wb") as f:
						content = urlopen(download_url).read()
						f.write(content)
						f.flush()
						print("done", flush=True)
				else:
					print("Skipping download: '%s' as file already exists in directory: '%s'" % (
						filename, album_name))
		else:
			print("Nothing found")
			
		print()

	print("ALL DOWNLOADS COMPLETE")
