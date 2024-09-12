import textwrap

from bs4 import BeautifulSoup, Tag, NavigableString


def parse_soup_from_xml(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')


def retrieve_contents(tag: Tag, ignored_child_tag_names: list[str] = ()) -> str:
    """
    Return all the HTML contents of the specified tag
    Excludes the contents of specific sub-tags.
    """
    return textwrap.dedent(
        ''.join(
            str(c)
            for c in tag.contents
            if isinstance(c, NavigableString)
            or (isinstance(c, Tag) and c.name not in ignored_child_tag_names)
        )
    )
