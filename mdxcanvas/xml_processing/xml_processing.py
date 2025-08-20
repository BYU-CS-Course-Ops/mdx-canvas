from pathlib import Path
from typing import Callable

from ..resources import ResourceManager
from ..util import parse_soup_from_xml


def preprocess_xml(
        parent: Path,
        text: str,
        tag_preprocessors,
        resources: ResourceManager,
        process_file: Callable
) -> str:
    """
    Preprocess the XML/HTML text to handle special content tags
    e.g. links, images, files, includes, etc.

    Returns modified XML that uses local IDs in the links.
    These IDs will be replaced with real Canvas IDs during deployment.
    """

    soup = parse_soup_from_xml(text)
    _walk_xml(soup, tag_preprocessors)

    return str(soup)


def process_canvas_xml(tag_processors, text: str):
    """
    Process XML/HTML text into a DTOs that represent
    the content to be deployed to Canvas.

    :param text: The XML/HTML text to be processed
    :returns: Populated ResourceManager
    """

    # -- Strategy --
    # The algorithm walks the tree and calls the appropriate processor on each tag
    # Each custom tag is processed by a bespoke processor
    # The tag processor returns Canvas JSON
    # If the tag is not processed (no assigned processor),
    #  the algorithm recurses on its children

    soup = parse_soup_from_xml(text)
    _walk_xml(soup, tag_processors)

    return resources
