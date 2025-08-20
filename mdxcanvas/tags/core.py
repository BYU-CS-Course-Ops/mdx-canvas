from pathlib import Path

from bs4 import Tag, BeautifulSoup


class TagProcessor:
    priority: float
    """
    Lower priority processors run first
    In general, tags that have content should
      have a priority of at least 20.
    Tags that modify content should have a priority < 20.
    Default value is 15.
    """

    def __init__(self, priority: float = 15):
        self.priority = priority

    def handles_soup(self, soup: BeautifulSoup) -> bool:
        """Returns True if this processor should process the soup as a whole"""
        return False

    def process_soup(self, soup: BeautifulSoup, parent: Path) -> BeautifulSoup:
        return soup

    def handles_tag(self, tag: Tag) -> bool:
        """Returns True if this processor should process this tag"""
        return False

    def process_tag(self, tag: Tag, parent: Path) -> list[Tag]:
        """Returns tags that should replace the current tag"""
        return []


def process_xml(soup: BeautifulSoup, parent: Path, tag_processors: list[TagProcessor]):
    """
    Iterates through the tag_processors in linearized order
    """
    sorted_processors = list(sorted(tag_processors, key=lambda tp: tp.priority))
    _process_xml(soup, parent, sorted_processors)


def _process_xml(tag, parent: Path, tag_processors: list[TagProcessor], is_soup=True):
    for i, processor in enumerate(tag_processors):
        if is_soup and processor.handles_soup(tag):
            tag = processor.process_soup(tag, parent)

        elif processor.handles_tag(tag):
            _single_process_xml(tag, parent, processor, tag_processors[:i + 1])


def _single_process_xml(tag, parent: Path, tag_processor: TagProcessor, prior_processors: list[TagProcessor]):
    new_tags = tag_processor.process_tag(tag, parent)
    if new_tags:
        tag.replace(new_tags)
        # We need to catch up the new tags
        # They are processed with all the processors we've already seen
        for new_tag in new_tags:
            _process_xml(new_tag, parent, prior_processors, is_soup=False)
    else:
        for child in tag.children:
            _single_process_xml(child, parent, tag_processor, prior_processors)
