import asyncio
import functools
import requests
import time
from urllib.request import urlopen
import re
from urllib.parse import urljoin
import os


ts = time.time()
loop = asyncio.get_event_loop()

homepage = "http://www.aidalive.com"
source = urlopen(homepage).read().decode()
links = sorted(set(re.findall(r'href="(.*?\.mp3)" title="Download Audio File"', source)))

def _(text):
	TEXT = re.sub(r"[\?!\-_]|\s{2,}", " ", text)
	TEXT = TEXT.replace("&amp;", "&").replace("&#39;", "'")
	return TEXT.strip()

def get_mp3(link):
	data = link.rsplit("/", 2)
	file = data[-1]

	try:
		album = data[-2]
	except:
		album = "unknown"

	if not os.path.exists("Albums"):
		os.mkdir("Albums")

	# await asyncio.sleep(0)

	albumPath = "Albums/%s" % _(album.lower())

	if not os.path.exists(albumPath):
		os.makedirs(albumPath)
		print("\n%s album created ..." % _(album))
	
	with open ("%s/%s" % (albumPath, _(file)), "wb") as mp3:
		content = urlopen(link).read()
		
		mp3.write(content)
		print("    %s downloaded" % file)


@asyncio.coroutine
def do_checks(urls, homepage=homepage):
	futures = []
	for url in urls:
		url = urljoin(homepage, url)
		futures.append(loop.run_in_executor(None, functools.partial(get_mp3, url)))

	for req in asyncio.as_completed(futures):
		resp = yield from req

loop.run_until_complete(do_checks(links))
te = time.time()
print("Version A: " + str(te - ts))
