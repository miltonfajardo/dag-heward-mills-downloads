import re
import os
from urllib.request import urlopen

homepage = "http://www.aidalive.com"

def getSource(link, dec=True):
	if dec == False:
		return urlopen(link).read()
	return urlopen(link).read().decode()

def _(text):
	TEXT = re.sub(r":|\?|!|\s{2,}|-", " ", text)
	return TEXT.strip()

def getMp3(link):
	data = link.rsplit("/", 2)
	file = data[-1]
	try:
		album = data[-2]
	except:
		album = "unknown"

	if not os.path.exists("Albums"):
		os.mkdir("Albums")

	albumPath = "Albums/%s" % _(album).title()
	if not os.path.exists(albumPath):
		os.mkdir(albumPath)
		print("\n%s album created ..." % _(album))

	with open ("%s/%s" % (albumPath, _(file)), "wb") as mp3:
		mp3.write(getSource(link, False))
		print("    %s downloaded" % file)


source = getSource(homepage)
links = sorted(set(re.findall(r'href="(.*?\.mp3)" title="Download Audio File"', source)))

for x in links:
	try:
		getMp3(x)
	except Exception as err:
		print("Error: (%s) while downloading from %s" % (err, x))
