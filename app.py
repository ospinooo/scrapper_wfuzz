"""Script Crawler Wfuzz Content discovery

Authors:
    Pablo Ospino
    Illia Nechesa

"""
import re
import sys
import time
import wfuzz
import requests
import signal
import csv
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup


LOG = open(f"logs/{int(time.time())}.log", "w")
URL = sys.argv[1]


def is_url(tag):
    """
        Check if the tag is an actual website url.
    """
    return "href" in tag.attrs and tag["href"].startswith("http")


def get_url_references(url: str):
    """
        Gets an url and returns a list of referenced urls.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    all_as = soup.findAll('a')  # Every line of code with a tag

    r = re.compile(r"^(http.*:\/\/.+\.[^\/\?]+(\.[^\/\?]+)?)")  # Regex

    urls = []
    for tag in all_as:
        if is_url(tag):  # Just urls
            try:
                urls.append(r.search(tag["href"]).group(1))
            except:
                print(tag["href"])
                print(r.search(tag["href"]))

    return urls


def attack_url(url):
    """
        Gets an url
    """
    # pattern = r"FUZZ"
    print(f"\tUnknown Content discovery: {url}")
    LOG.write(f"\tUnknown Content discovery: {url}\n")
    i = 0
    for r in wfuzz.fuzz(hc=[404], url=f"{url}", payloads=[("file", dict(fn="wordlist/general/common.txt"))]):
        LOG.write(str(r) + "\n")
        i += 1
        # if i < 20:
        print(r)
        # url = re.sub(pattern, r.description, url)
    return i


urls_viewed = {}

f = open("n_url_queue.txt", "w")


def handle_exit(s, e):
    with open('output.csv', "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(urls_viewed.keys()))
        writer.writerow(list(urls_viewed.values()))
    f.close()
    LOG.close()


if __name__ == "__main__":
    # Handle exit
    signal.signal(signal.SIGINT, handle_exit)

    urls_queue = []
    urls_queue.append(URL)

    while len(urls_queue) > 0:
        # New to view
        url = urls_queue.pop()

        if url not in urls_viewed:
            # Add the keyword to the url's end.
            url_fuzz = urllib.parse.urljoin(url, 'FUZZ')

            # Attack!
            attacks = attack_url(url_fuzz)
            urls_viewed[url] = attacks  # Save succesful attacks

            # More references
            urls_queue += [u for u in get_url_references(url)]

            urls_queue = list(set(urls_queue))  # Delete duplicates
            print(urls_queue)  # Show queue

            f.write(f"{len(urls_queue)}\n")

    LOG.close()
