from bs4 import BeautifulSoup


def parse_xml(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')
