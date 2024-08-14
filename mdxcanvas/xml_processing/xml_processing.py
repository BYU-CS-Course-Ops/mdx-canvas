from pathlib import Path

from bs4 import BeautifulSoup

from mdxcanvas.inline_styling import bake_css
from mdxcanvas.resources import ResourceManager
from mdxcanvas.xml_processing.tag_preprocessors import make_image_preprocessor, make_file_preprocessor, make_zip_preprocessor
from mdxcanvas.xml_processing.quiz_tags import QuizTagProcessor

PageTagProcessor = lambda x: None
AssignmentTagProcessor = lambda x: None
ModuleTagProcessor = lambda x: None


def _walk_xml(tag, tag_processors):
    if not hasattr(tag, 'children'):
        return
    for child in tag.children:
        if hasattr(child, 'name') and child.name in tag_processors:
            processor = tag_processors[child.name]
            processor(child)
        _walk_xml(child, tag_processors)


def _preprocess_xml(parent: Path, text: str, resources: ResourceManager, global_css: str) -> str:
    """
    Preprocess the XML/HTML text to handle special content tags
    e.g. links, images, files, includes, etc.

    Returns modified XML that uses local IDs in the links.
    These IDs will be replaced with real Canvas IDs during deployment.
    """
    tag_processors = {
        'img': make_image_preprocessor(parent, resources),
        'file': make_file_preprocessor(parent, resources),
        'zip': make_zip_preprocessor(parent, resources)
    }

    soup = BeautifulSoup(text, 'html.parser')
    _walk_xml(soup, tag_processors)

    # Post-process the XML
    # - bake in CSS styles
    xml_postprocessors = [
        lambda s: bake_css(s, global_css)
    ]
    for xml_post in xml_postprocessors:
        soup = xml_post(soup)

    return str(soup)


def _process_xml(text: str, resources: ResourceManager):
    """
    Process XML/HTML text into a DTOs that represent
    the content to be deployed to Canvas.

    :param parent: The Path to the parent folder of the content
    :param text: The XML/HTML text to be processed
    :returns: Populated ResourceManager
    """

    # -- Strategy --
    # The algorithm walks the tree and calls the appropriate processor on each tag
    # Each custom tag is processed by a bespoke processor
    # The tag processor returns Canvas JSON
    # If the tag is not processed (no assigned processor),
    #  the algorithm recurses on it's children

    tag_processors = {
        'quiz': QuizTagProcessor(resources),
        'page': PageTagProcessor(resources),
        'assignment': AssignmentTagProcessor(resources),
        'module': ModuleTagProcessor(resources)
    }

    soup = BeautifulSoup(text, 'html.parser')
    _walk_xml(soup, tag_processors)

    return resources


def process_xml(parent: Path, text: str, global_css: str) -> ResourceManager:
    resources = ResourceManager()

    text = _preprocess_xml(parent, text, resources, global_css)
    _process_xml(text, resources)

    return resources
