import requests
from bs4 import BeautifulSoup


def get_text_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    clean_lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            clean_lines.append(line)

    return "\n".join(clean_lines)