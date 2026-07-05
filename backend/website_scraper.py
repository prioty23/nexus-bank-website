import requests
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urljoin, urlparse


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_text_from_website(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    clean_lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            clean_lines.append(line)

    return "\n".join(clean_lines)


def get_internal_links_from_website(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    seen_urls = set()

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(url, anchor["href"])
        absolute_url = urldefrag(absolute_url)[0]
        parsed_url = urlparse(absolute_url)

        if parsed_url.scheme not in ["http", "https"]:
            continue

        if not parsed_url.netloc.endswith("ebl.com.bd"):
            continue

        if absolute_url in seen_urls:
            continue

        seen_urls.add(absolute_url)
        link_text = " ".join(anchor.get_text(" ", strip=True).split())

        links.append({
            "url": absolute_url,
            "text": link_text,
        })

    return links
