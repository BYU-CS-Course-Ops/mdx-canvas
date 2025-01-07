import dataclasses
from datetime import datetime
from typing import Callable, Any

from bs4 import Tag

from ..our_logging import get_logger
from ..util import retrieve_contents

logger = get_logger()


def parse_date(date: datetime | str | None) -> str:
    if isinstance(date, datetime):
        return datetime.isoformat(date)

    elif isinstance(date, str):
        # Check if the string is already in ISO format
        try:
            return datetime.isoformat(datetime.fromisoformat(date))
        except ValueError:
            pass

        try_formats = [
            "%b %d, %Y, %I:%M %p",
            "%b %d %Y %I:%M %p",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
        for format_str in try_formats:
            try:
                parsed_date = datetime.strptime(date, format_str)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Invalid date format: {date}")

        # Convert the parsed datetime object to the desired timezone
        # to_zone = pytz.timezone(time_zone)
        # parsed_date = parsed_date.replace(tzinfo=None)  # Remove existing timezone info
        # parsed_date = parsed_date.astimezone(to_zone)
        # TODO - Move this timezone block to deployment
        return datetime.isoformat(parsed_date)
    else:
        raise TypeError("Date must be a datetime object or a string")


def parse_int(text):
    return int(text)


def parse_bool(text):
    # Forgiving boolean parser
    if isinstance(text, bool):
        return text

    if text.lower() == "true":
        return True
    elif text.lower() == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean value: {text}")


def parse_list(text):
    items = text.strip().split(',')
    return [cell.strip() for cell in items if cell.strip()]


def parse_dict(text):
    # Assumes the string is a comma-separated list of key-value pairs
    # Example: "key1=value1, key2=value2 "
    return dict(cell.strip().split('=') for cell in text.split(',') if cell.strip())


@dataclasses.dataclass
class Attribute:
    name: str
    default: Any = None
    parser: Callable[[str], Any] = lambda x: x
    new_name: str = None
    required: bool = False
    ignore: bool = False
    is_tag: bool = False


def get_tag_info(tag: Tag):
    name = tag.name
    hint = tag.get('title', None)
    if hint is None:
        hint = tag.get('name', None)
    display = name
    if hint is not None:
        display += f'({hint})'
    return display


def get_tag_path(tag: Tag):
    tokens = [get_tag_info(tag)] + [get_tag_info(p) for p in tag.parents]
    return '.'.join(tokens[::-1])


def parse_settings(tag: Tag, attributes: list[Attribute]):
    settings = {}
    processed_fields = set()

    for attribute in attributes:
        try:

            processed_fields.add(attribute.name)
            if attribute.new_name:
                processed_fields.add(attribute.new_name)
            name = attribute.new_name or attribute.name

            if attribute.ignore:
                continue

            if (field := (
                    tag.get(attribute.name, None)
                    or tag.get(attribute.new_name, None)
            )) is not None:
                # Parse the value
                value = attribute.parser(field)
                settings[name] = value

            elif attribute.is_tag:
                child = tag.find(attribute.name, recursive=False)
                value = retrieve_contents(child)
                settings[name] = attribute.parser(value)

            elif attribute.default is not None:
                settings[name] = attribute.default

            elif attribute.required:
                raise Exception(f'Required field {attribute.name} missing from tag {tag.name}')
        except:
            logger.exception(f"Error processing attribute {attribute.name} in tag {get_tag_path(tag)}")
            raise

    for key in tag.attrs:
        if key not in processed_fields:
            logger.warning(f'Unprocessed_fields field {key} @ {get_tag_path(tag)}')

    return settings


def parse_children_tag_contents(tag: Tag, child_name):
    children = tag.find_all(child_name, recursive=False)
    return [retrieve_contents(child) for child in children]
