#!/usr/bin/env python
# 15:04.16 total
from urllib.request import urlopen, urlretrieve
from urllib import request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, SoupStrainer
import eyed3
import random
import time


def get_urls(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    urls = []
    urlroot = 0
    for child in root.find('urls').findall('url'):
        urls.append(child.text)
    return urls


def get_depth(xml):
    tree = ET.parse(xml)
    root = tree.getroot()

    return root.find('depth').text


def get_html(url):
    req = request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    return urlopen(req).read()


def get_all_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    return links


def get_all_sounds(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('audio'):
        links.append(link.get('src'))
    for link in soup.find_all('a'):
        if not link.get("href"):
            continue
        if ".mp3" in link.get('href'):
            links.append(link.get('href'))
    return links


def process_audio(url):
    if url in seen:
        return
    seen.add(url)

    name = str(random.randint(1, 999999))+".mp3"

    print("Processing audio", url)
    req = request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/35.0.1916.47 Safari/537.36'
        })

    u = urlopen(req)
    f = open(name, 'wb')
    file_size = int(u.getheader("Content-Length")[0])
    while True:
        buffer = u.read(512)
        if not buffer:
            break
        time.sleep(0.0005)  # Simulate network throttle
        f.write(buffer)
    f.close()

    file = eyed3.load(name)
    print(file.tag.title, file.tag.genre.name)
    add_track(file.tag.title, file.tag.genre.name)


def process_url(url, depth):
    global seen
    if (depth == 0):
        return
    print("process_url " + url, " depth ", depth)
    html = get_html(url)
    links = get_all_links(html)

    for link in links:
        if not link:
            continue
        if "mp3" in link:
            continue
        if 'http' not in link:
            link = url+link
        add_url(link, int(depth)-1)

    mus = get_all_sounds(html)
    for m in mus:
        if 'mp3' not in m:
            continue
        if 'http' not in m:
            m = url+m

        try:
            process_audio(m)
        except Exception:
            pass


def add_url(url, depth):
    global urls2
    global seen

    if url in seen:
        return
    seen.add(url)
    urls2.append((url, int(depth)))


seen = set()
urls2 = []


def genxml():
    global genres

    root = ET.Element("genres")
    for genre in genres.keys():
        elem = ET.Element(genre)
        root.append(elem)
        for song in genres[genre]:
            sngelem = ET.Element("song")
            sngelem.text = song
            elem.append(sngelem)

    strtree = ET.tostring(root, 'utf-8')
    cont = ''+strtree.decode('utf-8')
    with open("out.xml", "w") as o:
        o.write(cont)


def main():
    global urls2
    urls = get_urls('data.xml')
    depth = get_depth('data.xml')
    print("Urls: ", ','.join(urls))
    print("Depth: ", depth)

    for url in urls:
        add_url(url, depth)

    while len(urls2) > 0:
        u = urls2.pop()
        try:
            process_url(u[0], u[1])
        except Exception as e:
            print("Broken url ", u[0], e)

    print(genres)
    genxml()


def add_track(name, genre):
    global genres
    if genre not in genres.keys():
        genres[genre] = []
    genres[genre].append(name)


genres = {}

if __name__ == "__main__":
    main()
