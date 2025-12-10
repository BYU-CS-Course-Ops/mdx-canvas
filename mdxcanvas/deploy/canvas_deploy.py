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
from .assignment import deploy_assignment
from .checksums import MD5Sums, compute_md5
from .course_settings import deploy_settings
from .file import deploy_file
from .group import deploy_group
from .module import deploy_module
from .override import deploy_override
from .page import deploy_page
from .quiz import deploy_quiz
from .syllabus import deploy_syllabus
from .zip import deploy_zip, predeploy_zip
from ..generate_result import MDXCanvasResult
from ..our_logging import log_warnings, get_logger
from ..resources import CanvasResource, iter_keys, ResourceInfo

logger = get_logger()


def deploy_resource(course: Course, resource_type: str, resource_data: dict) -> tuple[ResourceInfo, tuple[str, str] | None]:
    deployers: dict[str, Callable[[Course, dict], tuple[ResourceInfo, tuple[str, str] | None]]] = {
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
        try:
            canvas_info = resource_objs.get((rtype, rid), md5s.get_canvas_info((rtype, rid)))
        except Exception as ex:
            logger.error(f'Error getting canvas info for {rtype} {rid}: {ex}. '
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

        item = (resource['type'], resource['id'])

        stored_md5 = md5s.get_checksum(item)
        current_md5 = compute_md5(resource_data)

        logger.debug(f'MD5 {resource_key}: {current_md5} vs {stored_md5}')

        # Attach the Canvas object id (stored as `canvas_id`) to the resource data
        # so deployment can detect whether to create a new item or update an existing one.
        resource['data']['canvas_id'] = md5s.get_canvas_info(item).get('id') if md5s.has_canvas_info(item) else None

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


def _create_shell_data(resource_type: str, original_data: dict) -> dict:
    """Create shell data based on resource type"""
    if resource_type == 'page':
        from .page import create_page_shell
        return create_page_shell(original_data)
    elif resource_type == 'assignment':
        from .assignment import create_assignment_shell
        return create_assignment_shell(original_data)
    elif resource_type == 'quiz':
        from .quiz import create_quiz_shell
        return create_quiz_shell(original_data)
    else:
        raise ValueError(f'Shell creation not supported for type: {resource_type}')


def _deploy_single_resource(
    course: Course,
    resource_key: tuple[str, str],
    to_deploy: dict,
    md5s: MD5Sums,
    resource_objs: dict,
    resources: dict,
    result: MDXCanvasResult
):
    """Deploy a single resource (extracted from deployment loop)"""
    current_md5, resource = to_deploy[resource_key]
    rtype, rid = resource_key

    logger.info(f'Deploying {rtype} {rid}')

    if (resource_data := resource.get('data')) is not None:
        resource_data = update_links(md5s, resource_data, resource_objs)
        canvas_obj_info, info = deploy_resource(course, rtype, resource_data)

        try:
            url = canvas_obj_info['url']
            result.add_deployed_content(rtype, rid, url)
        except KeyError:
            logger.debug(f'Canvas {rtype} has no link to {rid}')

        if info:
            result.add_content_to_review(*info)

        md5s[resource_key] = {
            "checksum": current_md5,
            "canvas_info": canvas_obj_info
        }

        resource_objs[resource_key] = canvas_obj_info


def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource], result: MDXCanvasResult, dryrun=False):
    resource_dependencies = get_dependencies(resources)
    logger.debug(f'Dependency graph: {resource_dependencies}')

    resource_order, shell_candidates = linearize_dependencies(resource_dependencies, resources)
    logger.debug(f'Linearized dependencies: {resource_order}')

    # Track shell data for cycle resolution
    shell_data = {}  # Maps (type, id) -> original data dict
    shell_keys = set()

    if shell_candidates:
        logger.info(f'Detected {len(shell_candidates)} shell candidates for cycle resolution')
        for resource_key, resource in shell_candidates:
            logger.info(f'  - Shell candidate: {resource_key[0]} {resource_key[1]}')
            if resource['data'] is not None:
                # Store original data
                shell_data[resource_key] = resource['data'].copy()
                shell_keys.add(resource_key)

                # Replace with shell data
                resource['data'] = _create_shell_data(resource_key[0], resource['data'])

    warnings = []
    logger.info('Beginning deployment to Canvas')
    with MD5Sums(course) as md5s, TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        predeploy_resources(resources, timezone, tmpdir)

        to_deploy = identify_modified_or_outdated(resources, resource_order, resource_dependencies, md5s)

        # Ensure shell candidates are always deployed (even if not modified)
        if shell_keys:
            for resource_key in shell_keys:
                if resource_key not in to_deploy:
                    resource = resources[resource_key]
                    if resource.get('data') is not None:
                        current_md5 = compute_md5(resource['data'])
                        to_deploy[resource_key] = (current_md5, resource)
                        logger.info(f'Added shell candidate to deployment: {resource_key[0]} {resource_key[1]}')

        logger.info('Items to deploy:')
        for rtype, rid in to_deploy.keys():
            logger.info(f' - {rtype} {rid}')

        if dryrun:
            return

        resource_objs: dict[tuple[str, str], CanvasObject] = {}

        # PHASE 1: Deploy shells for cycle resolution
        if shell_keys:
            logger.info('=== Phase 1: Deploying shells for cycle resolution ===')
            for resource_key in shell_keys:
                if resource_key in to_deploy:
                    try:
                        logger.debug(f'Processing shell {resource_key}')
                        _deploy_single_resource(course, resource_key, to_deploy, md5s, resource_objs, resources, result)
                    except Exception as ex:
                        rtype, rid = resource_key
                        error = f'Error deploying shell {rtype} {rid}: {str(ex)}'
                        logger.error(error)
                        result.add_error(error)
                        result.output()
                        raise

        # PHASE 2: Deploy remaining resources
        logger.info('=== Phase 2: Deploying remaining resources ===')
        for resource_key in to_deploy:
            if resource_key not in shell_keys:
                try:
                    logger.debug(f'Processing {resource_key}')
                    _deploy_single_resource(course, resource_key, to_deploy, md5s, resource_objs, resources, result)
                except Exception as ex:
                    rtype, rid = resource_key
                    error = f'Error deploying resource {rtype} {rid}: {str(ex)}'
                    logger.error(error)
                    result.add_error(error)
                    result.output()
                    raise

        # PHASE 3: Update shells with full content
        if shell_keys:
            logger.info('=== Phase 3: Updating shells with actual content ===')
            for resource_key in shell_keys:
                if resource_key in shell_data:
                    try:
                        # Restore original data
                        resource = resources[resource_key]
                        original_data = shell_data[resource_key].copy()

                        # Get the canvas_id from the shell deployment in Phase 1
                        if resource_key in resource_objs:
                            shell_canvas_info = resource_objs[resource_key]
                            canvas_id_value = shell_canvas_info.get('id')
                            logger.info(f'Shell canvas info: {shell_canvas_info}')
                            logger.info(f'Setting canvas_id to: {canvas_id_value}')
                            original_data['canvas_id'] = canvas_id_value
                        else:
                            logger.warning(f'Resource {resource_key} not found in resource_objs - shell may not have been deployed')

                        # Update links
                        original_data = update_links(md5s, original_data, resource_objs)

                        # Redeploy with full content
                        rtype, rid = resource_key
                        logger.info(f'Updating shell: {rtype} {rid} (canvas_id: {original_data.get("canvas_id")})')
                        canvas_obj_info, info = deploy_resource(course, rtype, original_data)

                        # Update resource data with final version
                        resource['data'] = original_data

                        # Update result
                        try:
                            url = canvas_obj_info['url']
                            result.add_deployed_content(rtype, rid, url)
                        except KeyError:
                            logger.debug(f'Canvas {rtype} has no link to {rid}')

                        if info:
                            result.add_content_to_review(*info)

                        # Update MD5
                        current_md5 = compute_md5(resource['data'])
                        md5s[resource_key] = {
                            "checksum": current_md5,
                            "canvas_info": canvas_obj_info
                        }
                    except Exception as ex:
                        error = f'Error updating shell {rtype} {rid}: {str(ex)}'
                        logger.error(error)
                        result.add_error(error)
                        result.output()
                        raise

        if result.get_content_to_review():
            for content in result.get_content_to_review():
                warnings.append(content)
            log_warnings(warnings)
    # Done!
