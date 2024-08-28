import textwrap

from bs4 import BeautifulSoup, Tag, NavigableString


def parse_soup_from_xml(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')


def retrieve_contents(tag: Tag, children_tag_names: list[str] = ()) -> str:
    """
    Return all the HTML contents of the specified tag
    Excludes the contents of specific sub-tags.
    """
    if not children_tag_names:
        return ''.join(str(c) for c in tag.contents)

    return textwrap.dedent(''.join(str(c) for c in tag.contents if isinstance(c, NavigableString) or (isinstance(c, Tag) and c.name not in children_tag_names)))
