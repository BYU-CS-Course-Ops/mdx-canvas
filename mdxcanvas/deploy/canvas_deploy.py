import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pytz
from canvasapi.canvas_object import CanvasObject
from canvasapi.course import Course
from pkg_resources import resource_listdir

from .algorithms import linearize_dependencies
from .announcement import deploy_announcement, lookup_announcement
from .assignment import deploy_assignment, lookup_assignment
from .checksums import MD5Sums, compute_md5
from .file import deploy_file, lookup_file
from .module import deploy_module, lookup_module
from .override import deploy_override, lookup_override
from .page import deploy_page, lookup_page
from .quiz import deploy_quiz, lookup_quiz
from .syllabus import deploy_syllabus, lookup_syllabus
from .util import get_canvas_uri
from .zip import deploy_zip, lookup_zip, predeploy_zip
from ..generate_result import MDXCanvasResult
from ..our_logging import log_warnings, get_logger
from ..resources import CanvasResource, iter_keys

logger = get_logger()


def deploy_resource(course: Course, resource_type: str, resource_data: dict) -> tuple[CanvasObject, str | None]:
    deployers: dict[str, Callable[[Course, dict] , tuple[CanvasObject, str | None]]] = {
        'zip': deploy_zip,
        'file': deploy_file,
        'page': deploy_page,
        'quiz': deploy_quiz,
        'assignment': deploy_assignment,
        'override': deploy_override,
        'module': deploy_module,
        'syllabus': deploy_syllabus,
        'announcement': deploy_announcement
    }

    if (deploy := deployers.get(resource_type, None)) is None:
        raise Exception(f'Deployment unsupported for resource of type {resource_type}')

    try:
        deployed, info = deploy(course, resource_data)
    except:
        logger.error(f'Failed to deploy resource: {resource_type} {resource_data}')
        raise

    if deployed is None:
        raise Exception(f'Resource not found: {resource_type} {resource_data}')

    return deployed, info


def lookup_resource(course: Course, resource_type: str, resource_name: str) -> CanvasObject:
    finders: dict[str, Callable[[Course, str], CanvasObject]] = {
        'zip': lookup_zip,
        'file': lookup_file,
        'page': lookup_page,
        'quiz': lookup_quiz,
        'assignment': lookup_assignment,
        'override': lookup_override,
        'module': lookup_module,
        'syllabus': lookup_syllabus,
        'announcement': lookup_announcement
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
        if attr not in data or data.get(attr) is None:
            continue

        datetime_version = datetime.fromisoformat(make_iso(data[attr], time_zone))
        utc_version = datetime_version.astimezone(pytz.utc)
        data[attr] = utc_version.isoformat()


def get_dependencies(resources: dict[tuple[str, str], CanvasResource]) -> dict[tuple[str, str], list[tuple[str, str]]]:
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
        logger.debug(f'Predeploying {rtype} {resource_data}')
        resource_data = predeploy(resource_data, tmpdir)

    return resource_data


def identify_modified_or_outdated(
        resources: dict[tuple[str, str], CanvasResource],
        linearized_resources: list[tuple[str, str]],
        resource_dependencies: dict[tuple[str, str], list[tuple[str, str]]],
        md5s: MD5Sums
) -> dict[tuple[str, str], tuple[str, CanvasResource]]:
    """
    A resource is modified or outdated if:
    - It is new
    - It has changed its own data
    - It depends on another resource with a new ID (a file)
    """
    modified = {}

    for resource_key in linearized_resources:
        resource = resources[resource_key]
        if (resource_data := resource.get('data')) is None:
            # Just a resource reference
            continue

        stored_md5 = md5s.get(resource_key)
        current_md5 = compute_md5(resource_data)

        logger.debug(f'MD5 {resource_key}: {current_md5} vs {stored_md5}')

        if stored_md5 != current_md5:
            # New or changed data
            modified[resource_key] = current_md5, resource
            continue

        for dep_type, dep_name in resource_dependencies[resource_key]:
            if dep_type in ['file', 'zip'] and (dep_type, dep_name) in modified:
                modified[resource_key] = current_md5, resource
                break

    return modified


def predeploy_resources(resources, timezone, tmpdir):
    for resource_key, resource in resources.items():
        if resource.get('data') is not None:
            resource['data'] = predeploy_resource(resource['type'], resource['data'], timezone, tmpdir)


def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource], result: MDXCanvasResult, dryrun=False):
    resource_dependencies = get_dependencies(resources)
    logger.debug(f'Dependency graph: {resource_dependencies}')

    resource_order = linearize_dependencies(resource_dependencies)
    logger.debug(f'Linearized dependencies: {resource_order}')

    warnings = []
    logger.info('Beginning deployment to Canvas')
    with MD5Sums(course) as md5s, TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        predeploy_resources(resources, timezone, tmpdir)

        to_deploy = identify_modified_or_outdated(resources, resource_order, resource_dependencies, md5s)

        logger.info('Items to deploy:')
        for rtype, rname in to_deploy.keys():
            logger.info(f' - {rtype} {rname}')

        if dryrun:
            return

        resource_objs: dict[tuple[str, str], CanvasObject] = {}
        for resource_key, (current_md5, resource) in to_deploy.items():
            try:
                logger.debug(f'Processing {resource_key}')

                rtype, rname = resource_key
                logger.info(f'Processing {rtype} {rname}')
                if (resource_data := resource.get('data')) is not None:
                    resource_data = update_links(course, resource_data, resource_objs)

                    logger.info(f'Deploying {rtype} {rname}')

                    resource_obj, info = deploy_resource(course, rtype, resource_data)

                    url = resource_obj.html_url if hasattr(resource_obj, 'html_url') else None
                    result.add_deployed_content(rtype, rname, url)

                    if info:
                        result.add_content_to_review(*info)
                    resource_objs[resource_key] = resource_obj
                    md5s[resource_key] = current_md5
            except Exception as ex:
                error = f'Error deploying resource {rtype} {rname}: {str(ex)}'

                logger.error(error)

                result.add_error(error)
                result.output()
                raise

        if result.get_content_to_review():
            for content in result.get_content_to_review():
                warnings.append(content)
            log_warnings(warnings)
    # Done!
