import json
from datetime import datetime
from typing import Callable

import pytz
from canvasapi.course import Course

from .file import deploy_file, lookup_file
from .zip import deploy_zip, lookup_zip
from .quiz import deploy_quiz, lookup_quiz
from ..algorithms import linearize_dependencies
from ..resources import CanvasResource


# TODO - actually implement these
def nope(c, cd):
    raise NotImplementedError()


deploy_page = nope
deploy_assignment = nope
deploy_module = nope
lookup_page = nope
lookup_assignment = nope
lookup_module = nope


def deploy_resource(course: Course, resource_type: str, resource_data: dict) -> str:
    deployers: dict[str, Callable[[Course, dict], str]] = {
        'zip': deploy_zip,
        'file': deploy_file,
        'page': deploy_page,
        'quiz': deploy_quiz,
        'assignment': deploy_assignment,
        'module': deploy_module
    }

    if (deploy := deployers.get(resource_type, None)) is None:
        raise Exception(f'Deployment unsupported for resource of type {resource_type}')

    return deploy(course, resource_data)


def lookup_resource(course: Course, resource_type: str, resource_name: str) -> str:
    finders: dict[str, Callable[[Course, str], str]] = {
        'zip': lookup_zip,
        'file': lookup_file,
        'page': lookup_page,
        'quiz': lookup_quiz,
        'assignment': lookup_assignment,
        'module': lookup_module
    }

    if (finder := finders.get(resource_type, None)) is None:
        raise Exception(f'Lookup unsupported for resource of type {resource_type}')

    return finder(course, resource_name)


def update_links(data: dict, resource_uris) -> dict:
    text = json.dumps(data)
    for key, uri in resource_uris.items():
        text = text.replace(key, uri)
    return json.loads(text)


def make_iso(date: datetime | str | None, time_zone: str) -> str:
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
        to_zone = pytz.timezone(time_zone)
        parsed_date = parsed_date.replace(tzinfo=None)  # Remove existing timezone info
        parsed_date = parsed_date.astimezone(to_zone)
        return datetime.isoformat(parsed_date)
    else:
        raise TypeError("Date must be a datetime object or a string")


def fix_dates(data, time_zone):
    for attr in ['due_at', 'unlock_at', 'lock_at', 'show_correct_answers_at']:
        if attr not in data:
            continue

        datetime_version = datetime.fromisoformat(make_iso(data[attr], time_zone))
        utc_version = datetime_version.astimezone(pytz.utc)
        data[attr] = utc_version.isoformat()


def deploy_to_canvas(course: Course, timezone: str, resources: dict[str, CanvasResource]):
    resource_strings = {key: str(value) for key, value in resources.items()}
    resource_order = linearize_dependencies(resource_strings)

    resource_uris = {}
    for resource_key in resource_order:
        resource = update_links(resources[resource_key], resource_uris)

        if (resource_data := resource.get('data')) is not None:
            # Deploy resource using data
            fix_dates(resource_data, timezone)
            resource_uri = deploy_resource(course, resource['type'], resource_data)
        else:
            # Retrieve resource from Canvas
            resource_uri = lookup_resource(course, resource['type'], resource['name'])

        resource_uris[resource_key] = resource_uri

    # Done!
