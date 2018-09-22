import functools
import json
import re
import os
import sys
import time
from urllib.parse import urljoin
from urllib.request import urlopen

import asyncio
import requests


ts = time.time()
loop = asyncio.get_event_loop()


def _(text):
	TEXT = re.sub(r"[\?!\-_]|\s{2,}", " ", text)
	TEXT = TEXT.replace("&amp;", "&").replace("&#39;", "'")
	return TEXT.strip()


def get_album_id(url):
	r = requests.get(url).text
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


def get_mp3(link):
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


@asyncio.coroutine
def do_checks(urls):
	futures = []
	for url in urls:
		futures.append(loop.run_in_executor(
			None, functools.partial(get_mp3, url)))

	for req in asyncio.as_completed(futures):
		resp = yield from req


album_info_url = "http://daghewardmillsaudio.org/index.php?option=com_muscol&task=get_album_songs&id={0}"
links = []

if len(sys.argv) == 1:
	if not os.path.isfile("links.txt"):
		with open("links.txt", "w") as f:
			f.write("# Please provide links that starts with 'http'. Anything else will be ignored\n")
			f.write("""http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/87-building-a-multiple-megachurch
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/86-loyalty-and-the-megachurch
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/85-strive-lawfully-for-a-megachurch
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/82-going-deeper-and-doing-more
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/83-double-mega-missionary-church
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/84-love-and-the-megachurch
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/77-the-dream-church
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/78-advancing-in-pergamos
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/79-the-work-of-the-ministry
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/81-1-000-micro-churches
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/73-the-message-of-sacrifice
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/74-what-is-your-life
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/75-victory-in-laodicea
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/76-pastors-of-thousands
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/80-building-a-3-demensional-mega-church
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/52-allos-another-of-the-same-kind
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/60-all-out
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/71-zogreo
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/72-the-mega-church
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/89-the-mysteries-of-god
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/88-grace-and-peace
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/50-the-presence
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/63-gates-and-roads
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/64-victory-in-pergamos
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/65-bema-the-place-of-final-sentence
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/66-kruptos-man
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/67-agree-on-the-way
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/68-how-to-survive-in-ephesus
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/61-preparation-of-the-gospel
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/62-barrenness-fruitfulness
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/58-others
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/90-missions-and-missionaries
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/91-church-planting
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/54-birthday-kee-waa
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/53-perfection
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/56-snake-junction
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/92-australia-1-000
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/93-take-up-your-cross
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/95-obedience-unto-death
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/55-busselisation-mega-church-2
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/49-apocalypse
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/48-spiritual-battles
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/70-the-lord-s-anointed
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/96-do-the-work-of-an-evangelist
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/44-i-and-the-children
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/45-not-a-novice
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/97-missions
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/38-warfare-keys
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/39-the-powers-of-a-cross
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/41-moses-and-associates
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/40-tell-them
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/42-the-sufferings-of-christ
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/36-mighty-foundations
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/37-finish-what-you-started
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/35-my-first-love
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/34-lay-power
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/33-the-blessings-of-abraham
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/26-that-my-house-may-be-filled
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/28-the-bag-of-seeds
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/32-predestination
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/31-why-are-you-not-a-missionary
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/30-tasters-partakers
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/29-the-privilege
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/27-if-you-love-the-lord
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/25-warnings-of-purpose
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/21-god-s-banquet
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/22-inexorability-in-the-missions
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/23-lord-i-know-you-need-somebody
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/24-volante
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/19-the-word-of-my-patience
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/20-seigneur-ait-petie
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/18-be-thou-faithful-unto-death
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/98-awake-o-sleeper
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/17-sweet-influences-of-the-holy-spirit
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/16-secrets-of-the-anointed-and-his-anointing
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/14-atmosphere
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/13-100-million-souls
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/12-the-beautiful-job
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/10-fight-a-good-fight
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/11-principles-of-war
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/9-wise-as-serpents
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/2-how-can-i-say-thanks
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/8-give-thyself-wholly
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/7-mission-europe
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/15-mission-america
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/5-mission-africa
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/6-mission-south-africa
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/4-who-is-he-that-overcomes-the-world
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/3-god-requireth-that-which-is-past
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/1-fulfil-your-ministry
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/116-expect-great-things
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/115-attempt-great-things-for-god
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/114-obligation-of-christians
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/128-obligations-of-christian-workers-10-000-children
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/117-ready-at-20
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/118-let-my-people
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/119-victory-in-laodecia
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/120-stir-it-up
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/121-where-is-the-flock-that-was-given-thee
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/122-a-super-mega-church
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/123-i-will-multiply-them-and-they-shall-not-be-few
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/124-army-of-hard-followers
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/125-a-small-one-shall-become-a-strong-nation
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/126-the-mountain-of-the-lords-house-shall-be-established-on-top-of-the-mountain
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/127-she-was-fruitful-and-full-of-branches-by-reason-of-many-waters
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/129-the-church-must-send-or-it-will-end
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/130-no-city-shall-be-too-strong-for-you
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/131-the-islands-shall-wait-for-you
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/132-zealously-affected
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/133-neutralize-the-curse
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/134-everything-by-prayer-nothing-without-prayer
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/149-labour-to-be-blessed
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/162-make-yourself-a-saviour-of-men
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/163-candle-in-the-dark
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/166-no-weeping-no-gnashing
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/168-the-reward-for-hard-work-is-more-work
http://daghewardmillsaudio.org/index.php/component/muscol/C/2-camps-the-machaneh/169-twenty-five-to-fifty""")
			
		print("links.txt file does not exist but has been created.") 
		print("Please provide all your download links there line by line")
		print()
		
	with open("links.txt") as f:
		links = filter(lambda x: x.strip().startswith(
			"http"), f.read().split("\n"))
		links = list(set(links))
elif len(sys.argv) > 1:
	links = [sys.argv[1]]


loop.run_until_complete(do_checks(links))
te = time.time()
print("Version A: " + str(te - ts))
