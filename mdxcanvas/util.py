from bs4 import BeautifulSoup, Tag


def parse_soup_from_xml(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')


def retrieve_contents(tag: Tag):
    """Return all the HTML contents of the specified tag"""
    return ''.join(str(c) for c in tag.children)
