from bs4 import BeautifulSoup


def parse_soup_from_xml(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')
