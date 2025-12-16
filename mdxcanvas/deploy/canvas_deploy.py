import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pytz
from canvasapi.canvas_object import CanvasObject
from canvasapi.course import Course

from .algorithms import linearize_dependencies
from .announcement import deploy_announcement
from .assignment import deploy_assignment, deploy_shell_assignment
from .checksums import MD5Sums, compute_md5
from .course_settings import deploy_settings
from .file import deploy_file
from .group import deploy_group
from .module import deploy_module
from .override import deploy_override
from .page import deploy_page, deploy_shell_page
from .quiz import deploy_quiz, deploy_shell_quiz
from .syllabus import deploy_syllabus
from .zip import deploy_zip, predeploy_zip
from ..generate_result import MDXCanvasResult
from ..our_logging import log_warnings, get_logger
from ..resources import CanvasResource, iter_keys, ResourceInfo

logger = get_logger()

SHELL_DEPLOYERS = {
    #TODO: What other shell deployers are needed?
    'assignment': deploy_shell_assignment,
    'page': deploy_shell_page,
    'quiz': deploy_shell_quiz
}

DEPLOYERS = {
    'announcement': deploy_announcement,
    'assignment': deploy_assignment,
    'assignment_group': deploy_group,
    'course_settings': deploy_settings,
    'file': deploy_file,
    'module': deploy_module,
    'override': deploy_override,
    'page': deploy_page,
    'quiz': deploy_quiz,
    'syllabus': deploy_syllabus,
    'zip': deploy_zip
}


def deploy_resource(deployers: dict[str, Callable[[Course, dict], tuple[ResourceInfo, tuple[str, str] | None]]],
                    course: Course, resource_type: str, resource_data: dict) -> tuple[
    ResourceInfo, tuple[str, str] | None]:
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


def update_links(md5s: MD5Sums, data: dict, resource_objs: dict[tuple[str, str], CanvasObject]) -> dict:
    text = json.dumps(data)
    logger.debug(f'Updating links in {text}')

    for key, rtype, rid, field in iter_keys(text):
        logger.debug(f'Processing key: {key}, {rtype}, {rid}, {field}')

        # Get the canvas object if we just deployed it else check for it in the stored MD5s
        canvas_info = resource_objs.get((rtype, rid), md5s.get_canvas_info((rtype, rid)))

        if canvas_info is None:
            logger.error(f'Updating links in {text}')
            logger.error(f'No canvas info for {rtype} {rid}: '
                         f'Was not deployed in this run and not found in stored MD5s.')
            raise

        try:
            repl_text = canvas_info.get(field)
        except Exception as ex:
            logger.error(f'Error getting field {field} from canvas info for {rtype} {rid}: {ex}')
            raise

        if repl_text is None:
            raise Exception(f'Canvas {rtype}|{rid} has no {field}')

        text = text.replace(key, f'{repl_text}')

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
        for _, rtype, rid, _ in iter_keys(text):
            resource_key = (rtype, rid)
            deps[key].append(resource_key)
            if resource_key not in resources:
                missing_resources.append(resource_key)

    for rtype, rid in missing_resources:
        resources[rtype, rid] = CanvasResource(type=rtype, id=rid, data=None)

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
        linearized_resources: list[tuple[tuple[str, str], bool]],
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

    for resource_key, is_shell in linearized_resources:
        resource = resources[resource_key]
        if (resource_data := resource.get('data')) is None:
            # Just a resource reference
            continue

        item = (resource['type'], resource['id'])

        stored_md5 = md5s.get_checksum(item)
        current_md5 = compute_md5(resource_data)

        logger.debug(f'MD5 {resource_key}: {current_md5} vs {stored_md5}')

        # Attach the Canvas object id (stored as `canvas_id`) to the resource data
        # so deployment can detect whether to create a new item or update an existing one.
        resource['data']['canvas_id'] = md5s.get_canvas_info(item).get('id') if md5s.has_canvas_info(item) else None

        if stored_md5 is None:
            # New resource that needs to be deployed
            modified[resource_key, is_shell] = current_md5, resource
            continue

        if is_shell:
            # Shell deployments only needed for new resources
            # stored_md5 is not None, so the resource is not new
            # so we can skip
            continue

        if stored_md5 != current_md5:
            # Changed data, need to deploy
            modified[resource_key, is_shell] = current_md5, resource
            continue

        for dep_type, dep_name in resource_dependencies[resource_key]:
            if dep_type in ['file', 'zip'] and (dep_type, dep_name) in modified:
                modified[resource_key, is_shell] = current_md5, resource
                break

    return modified


def predeploy_resources(resources, timezone, tmpdir):
    for resource_key, resource in resources.items():
        if resource.get('data') is not None:
            resource['data'] = predeploy_resource(resource['type'], resource['data'], timezone, tmpdir)


def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource],
                     result: MDXCanvasResult, dryrun=False):
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
        for (rtype, rid), is_shell in to_deploy.keys():
            if is_shell:
                logger.info(f' - {rtype} {rid} (shell deployment)')
            else:
                logger.info(f' - {rtype} {rid}')

        if dryrun:
            return

        resource_objs: dict[tuple[str, str], CanvasObject] = {}
        for (resource_key, is_shell), (current_md5, resource) in to_deploy.items():
            try:
                logger.debug(f'Processing {resource_key}')

                rtype, rid = resource_key
                logger.info(f'Processing {rtype} {rid}')
                if (resource_data := resource.get('data')) is not None:
                    if is_shell:
                        logger.info(f'Deploying {rtype} {rid} (shell)')
                        canvas_obj_info, info = deploy_resource(SHELL_DEPLOYERS, course, rtype, resource_data)
                        # This line needed to ensure that the full deployment can find the canvas_id
                        # of the shell object
                        resource['data']['canvas_id'] = canvas_obj_info.get('id') if canvas_obj_info else None

                    else:
                        resource_data = update_links(md5s, resource_data, resource_objs)
                        logger.info(f'Deploying {rtype} {rid}')
                        canvas_obj_info, info = deploy_resource(DEPLOYERS, course, rtype, resource_data)

                    # noinspection PyTypedDict
                    # Many ResourceInfo types do have URL, but not all
                    if url := canvas_obj_info.get('url'):
                        result.add_deployed_content(rtype, rid, url)

                    if info:
                        result.add_content_to_review(*info)

                    md5s[resource_key] = {
                        "checksum": current_md5,
                        "canvas_info": canvas_obj_info
                    }

            except Exception as ex:
                error = f'Error deploying resource {rtype} {rid}: {str(ex)}'

                logger.error(error)

                result.add_error(error)
                result.output()
                raise

        if result.get_content_to_review():
            for content in result.get_content_to_review():
                warnings.append(content)
            log_warnings(warnings)
    # Done!
