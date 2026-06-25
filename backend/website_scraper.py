import requests
from bs4 import BeautifulSoup


def get_text_from_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
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