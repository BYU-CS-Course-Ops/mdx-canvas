import json
import logging

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pytz
from canvasapi.canvas_object import CanvasObject
from canvasapi.course import Course

from .algorithms import linearize_dependencies
from .checksums import MD5Sums, compute_md5
from .file import deploy_file, lookup_file
from .syllabus import deploy_syllabus, lookup_syllabus
from .util import get_canvas_uri, ResourceNotFoundException
from .zip import deploy_zip, lookup_zip, predeploy_zip
from .quiz import deploy_quiz, lookup_quiz
from .page import deploy_page, lookup_page
from .assignment import deploy_assignment, lookup_assignment
from .module import deploy_module, lookup_module

from ..resources import CanvasResource, iter_keys

logger = logging.getLogger('logger')


def deploy_resource(course: Course, resource_type: str, resource_data: dict) -> CanvasObject:
    deployers: dict[str, Callable[[Course, dict], CanvasObject]] = {
        'zip': deploy_zip,
        'file': deploy_file,
        'page': deploy_page,
        'quiz': deploy_quiz,
        'assignment': deploy_assignment,
        'module': deploy_module,
        'syllabus': deploy_syllabus
    }

    if (deploy := deployers.get(resource_type, None)) is None:
        raise Exception(f'Deployment unsupported for resource of type {resource_type}')

    try:
        deployed = deploy(course, resource_data)
    except:
        logging.error(f'Failed to deploy resource: {resource_type} {resource_data}')
        raise

    if deployed is None:
        raise Exception(f'Resource not found: {resource_type} {resource_data}')

    return deployed


def lookup_resource(course: Course, resource_type: str, resource_name: str) -> CanvasObject:
    finders: dict[str, Callable[[Course, str], CanvasObject]] = {
        'zip': lookup_zip,
        'file': lookup_file,
        'page': lookup_page,
        'quiz': lookup_quiz,
        'assignment': lookup_assignment,
        'module': lookup_module,
        'syllabus': lookup_syllabus
    }

    if (finder := finders.get(resource_type, None)) is None:
        raise Exception(f'Lookup unsupported for resource of type {resource_type}')

    found = finder(course, resource_name)

    if found is None:
        raise Exception(f'Resource not found: {resource_type} {resource_name}')

    return found


def update_links(course: Course, data: dict, resource_objs: dict[tuple[str, str], CanvasObject]) -> dict:
    text = json.dumps(data)
    logger.debug(f'Updating links in {text}')

    for key, rtype, rname, field in iter_keys(text):
        logger.debug(f'Processing key: {key}, {rtype}, {rname}, {field}')

        if (rtype, rname) not in resource_objs:
            logger.info(f'Retrieving {rtype} {rname}')
            resource_objs[rtype, rname] = lookup_resource(course, rtype, rname)

        obj = resource_objs[rtype, rname]
        if field == 'uri':
            repl_text = get_canvas_uri(obj)
        else:
            repl_text = str(getattr(obj, field))
        text = text.replace(key, repl_text)

    return json.loads(text)


def make_iso(date: datetime | str | None, time_zone: str) -> str:
    if isinstance(date, datetime):
        return datetime.isoformat(date)
    elif isinstance(date, str):
        try_formats = [
            "%b %d, %Y, %I:%M %p",
            "%b %d %Y %I:%M %p",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
        for format_str in try_formats:
            try:
                parsed_date = datetime.strptime(date, format_str)
                if parsed_date.tzinfo:
                    return datetime.isoformat(parsed_date)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Invalid date format: {date}")

        # Convert the parsed datetime object to the desired timezone
        to_zone = pytz.timezone(time_zone)
        localized_date = to_zone.localize(parsed_date)
        return datetime.isoformat(localized_date)
    else:
        raise TypeError("Date must be a datetime object or a string")


def fix_dates(data, time_zone):
    for attr in ['due_at', 'unlock_at', 'lock_at', 'show_correct_answers_at']:
        if attr not in data:
            continue

        datetime_version = datetime.fromisoformat(make_iso(data[attr], time_zone))
        utc_version = datetime_version.astimezone(pytz.utc)
        data[attr] = utc_version.isoformat()


def get_dependencies(resources: dict[tuple[str, str], CanvasResource]) -> dict[tuple[str, str], list[str]]:
    """Returns the dependency graph in resources. Adds missing resources to the input dictionary."""
    deps = {}
    missing_resources = []
    for key, resource in resources.items():
        deps[key] = []
        text = json.dumps(resource)
        for _, rtype, rname, _ in iter_keys(text):
            resource_key = (rtype, rname)
            deps[key].append(resource_key)
            if resource_key not in resources:
                missing_resources.append(resource_key)

    for rtype, rname in missing_resources:
        resources[rtype, rname] = CanvasResource(type=rtype, name=rname, data=None)

    return deps


def predeploy_resource(rtype: str, resource_data: dict, timezone: str, tmpdir: Path) -> dict:
    fix_dates(resource_data, timezone)

    predeployers: dict[str, Callable[[dict, Path], dict]] = {
        'zip': predeploy_zip
    }

    if (predeploy := predeployers.get(rtype)) is not None:
        resource_data = predeploy(resource_data, tmpdir)

    return resource_data


def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource]):
    resource_dependencies = get_dependencies(resources)
    logger.debug(f'Dependency graph: {resource_dependencies}')

    resource_order = linearize_dependencies(resource_dependencies)
    logger.debug(f'Order of deployment: {resource_order}')

    logger.info('-- Beginning deployment to Canvas --')
    with MD5Sums(course) as md5s, TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        resource_objs: dict[tuple[str, str], CanvasObject] = {}
        for resource_key in resource_order:
            logger.debug(f'Processing {resource_key}')
            resource = resources[resource_key]

            rtype = resource['type']
            rname = resource['name']

            if (resource_data := resource.get('data')) is not None:
                # Deploy resource using data
                resource_data = predeploy_resource(rtype, resource_data, timezone, tmpdir)
                resource_data = update_links(course, resource_data, resource_objs)

                stored_md5 = md5s.get(resource_key)
                current_md5 = compute_md5(resource_data)

                if current_md5 != stored_md5:
                    # Create the resource
                    logger.info(f'Deploying {rtype} {rname}')
                    resource_obj = deploy_resource(course, rtype, resource_data)
                    resource_objs[resource_key] = resource_obj
                    md5s[resource_key] = current_md5

    # Done!
