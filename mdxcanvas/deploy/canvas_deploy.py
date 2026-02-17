import time
import json
import re
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import defaultdict
from typing import Callable

import pytz
from canvasapi.exceptions import ResourceDoesNotExist
from canvasapi.canvas_object import CanvasObject
from canvasapi.course import Course

from .algorithms import linearize_dependencies
from .announcement import deploy_announcement
from .assignment import deploy_assignment, deploy_shell_assignment
from .checksums import MD5Sums, compute_md5
from .course_settings import deploy_settings
from .file import deploy_file
from .group import deploy_group
from .module import deploy_module, deploy_module_item, get_module_item
from .override import deploy_override, get_override
from .page import deploy_page, deploy_shell_page
from .quiz import deploy_quiz, deploy_quiz_question, deploy_quiz_question_order, deploy_shell_quiz, get_quiz_question
from .syllabus import deploy_syllabus
from .zip import deploy_zip, predeploy_zip
from ..deployment_report import DeploymentReport
from ..our_logging import get_logger
from ..resources import CanvasResource, iter_keys, ResourceInfo

from .migration import migrate

logger = get_logger()

PREDEPLOYERS: dict[str, Callable[[dict, Path], dict]] = {
    'zip': predeploy_zip
}

SHELL_DEPLOYERS: dict[str, Callable[[Course, dict], tuple[ResourceInfo, tuple[str, str] | None]]] = {
    # Current known resources that need shell deployments
    'assignment': deploy_shell_assignment,
    'page': deploy_shell_page,
    'quiz': deploy_shell_quiz
}

DEPLOYERS: dict[str, Callable[[Course, dict], tuple[ResourceInfo, tuple[str, str] | None]]] = {
    'announcement': deploy_announcement,
    'assignment': deploy_assignment,
    'assignment_group': deploy_group,
    'course_settings': deploy_settings,
    'file': deploy_file,
    'module': deploy_module,
    'module_item': deploy_module_item,
    'override': deploy_override,
    'page': deploy_page,
    'quiz': deploy_quiz,
    'quiz_question': deploy_quiz_question,
    'quiz_question_order': deploy_quiz_question_order,
    'syllabus': deploy_syllabus,
    'zip': deploy_zip
}


# =============================================================================
# Utility functions
# =============================================================================

def make_iso(date: datetime | str | None, time_zone: str) -> str:
    if isinstance(date, datetime):
        return datetime.isoformat(date)

    if isinstance(date, str):
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

        to_zone = pytz.timezone(time_zone)
        localized_date = to_zone.localize(parsed_date)
        return datetime.isoformat(localized_date)

    raise TypeError("Date must be a datetime object or a string")


def fix_dates(data: dict, time_zone: str, resource: CanvasResource):
    for attr in ['due_at', 'unlock_at', 'lock_at', 'show_correct_answers_at']:
        if (val := data.get(attr)) is None:
            continue

        try:
            dt = datetime.fromisoformat(make_iso(val, time_zone))
            data[attr] = dt.astimezone(pytz.utc).isoformat()
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid date format for {resource['type']} {resource['id']}\n  {attr}: '{val}'\n  in {resource['content_path']}") from e


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
        resources[rtype, rid] = CanvasResource(type=rtype, id=rid, data={}, content_path='')

    return deps


def update_links(md5s: MD5Sums, data: dict, resource_objs: dict, current_resource: CanvasResource) -> dict:
    text = json.dumps(data)

    for key, rtype, rid, field in iter_keys(text):
        canvas_info = resource_objs.get((rtype, rid)) or md5s.get_canvas_info((rtype, rid))

        if not canvas_info:
            logger.debug(data)
            raise ValueError(
                f"No canvas info for {rtype} {rid}\n  Referenced in {current_resource['type']} {current_resource['id']}\n  in {current_resource['content_path']}")

        if not (repl_text := canvas_info.get(field)):
            raise ValueError(
                f"Missing field '{field}' in {rtype} {rid}\n  Referenced in {current_resource['type']} {current_resource['id']}\n  in {current_resource['content_path']}")

        text = text.replace(key, str(repl_text))

    return json.loads(text)


def post_process_resource(resource_data) -> dict:
    """
    Post-processing involves changes that shouldn't be included
    when considering whether a resource has changed and should be redeployed.
    """
    text = json.dumps(resource_data)

    # <timestamp /> tags
    # Because we are searching in JSON, double quotes will be escaped with \
    while m := re.search(r'''<\s*timestamp\s*(?:format\s*=\s*(\\"|')([^"']*)\1)?\s*(\/>|>\s*<\/timestamp>)''', text):
        timestamp = datetime.now().strftime(m.group(2) or '%B %d, %Y at %I:%M %p')
        text = text.replace(m.group(0), timestamp)

    return json.loads(text)


def deploy_resource(deployers: dict, course: Course, rtype: str, data: dict, resource: CanvasResource) -> tuple[ResourceInfo, tuple[str, str] | None]:
    if not (deploy := deployers.get(rtype)):
        raise Exception(f"Unsupported resource type {rtype} {resource['id']}\n  in {resource['content_path']}")

    try:
        resource_info, info = deploy(course, data)
    except Exception as e:
        raise Exception(
            f"Error deploying {rtype} {resource['id']}\n  {type(e).__name__}: {e}\n  in {resource['content_path']}") from e

    if not resource_info:
        raise Exception(f"Deployment returned None for {rtype} {resource['id']}\n  in {resource['content_path']}")

    return resource_info, info


# =============================================================================
# Predeploy
# =============================================================================

def predeploy_resources(resources: dict, timezone: str, tmpdir: Path):
    for resource in resources.values():
        if (data := resource.get('data')) is None:
            continue

        fix_dates(data, timezone, resource)

        rtype = resource['type']
        if predeploy := PREDEPLOYERS.get(rtype):
            logger.debug(f'Predeploying {rtype} {data}')
            resource['data'] = predeploy(data, tmpdir)


# =============================================================================
# Identify modified/outdated resources
# =============================================================================

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

    Returns:
        dict: A dictionary mapping resource keys to their current MD5 and resource data.
            - Key: (resource_key, is_shell)
                - resource_key: (type, id)
                    - type: str, the resource type (e.g., 'assignment', 'page', etc.)
                    - id: str, the resource identifier that the user assigned (not the Canvas ID)
                - is_shell: bool, indicating if this is a shell deployment
                    - Unfortunately needed to handle shell deployments properly, otherwise shell deployments are
                      overwritten by full deployments of the same resource.
            - Value: (current_md5, resource)
                - current_md5: str, the current MD5 checksum of the resource data
                - resource: CanvasResource, the resource data itself
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
            logger.debug(f'MD5 {resource_key}: {current_md5} vs {stored_md5}')
            modified[resource_key, is_shell] = current_md5, resource
            continue

        for dep_type, dep_name in resource_dependencies[resource_key]:
            if dep_type in ['file', 'zip'] and (dep_type, dep_name) in modified:
                modified[resource_key, is_shell] = current_md5, resource
                break

    return modified


# =============================================================================
# Stale resource handling
# =============================================================================

def get_stale_resources(resources: dict[tuple[str, str], CanvasResource], md5s: MD5Sums) -> list[tuple[str, str, dict]]:
    stale = [
        (rtype, rid, canvas_info)
        for (rtype, rid), info in md5s.items()
        if (rtype, rid) not in resources and rtype not in ['syllabus', 'course_settings', 'quiz_question_order']
        if (canvas_info := md5s.get_canvas_info((rtype, rid)))
    ]

    priority = (lambda item:
                0 if item[0] == 'module_item' else
                1 if item[0] == 'quiz_question' else
                2 if item[0] == 'override' else
                3
                )

    return sorted(stale, key=priority)


def _lookup_stale_canvas_resource(course: Course, item_type: str, item_id: str,
                                  canvas_info: dict) -> CanvasObject | None:
    canvas_id = canvas_info.get('id')

    # Handle special case resources (i.e. those that require a parent object to look up the specific object

    if item_type in ['module_item', 'override', 'quiz_question']:
        if item_type == 'module_item':
            canvas_resource = get_module_item(course, canvas_info.get('module_id'), canvas_id)
        elif item_type == 'override':
            canvas_resource = get_override(course, canvas_info.get('assignment_id'), canvas_id)
        elif item_type == 'quiz_question':
            canvas_resource = get_quiz_question(course, canvas_info.get('quiz_id'), canvas_id)
        else:
            raise NotImplementedError(f"Unsupported stale resource type {item_type} {item_id}")

    else:
        # Standard Canvas API getters (course.get_assignment, course.get_page, etc.)
        if item_type == 'announcement':
            lookup = course.get_discussion_topic
        elif item_type == 'zip':
            lookup = course.get_file
        else:
            lookup = getattr(course, f'get_{item_type}', None)

        if not lookup:
            raise NotImplementedError(f"Unsupported stale resource type {item_type} {item_id}")
        canvas_resource = lookup(canvas_id)

    return canvas_resource


def remove_stale_resources(course: Course, stale: list[tuple[str, str, dict]], md5s: MD5Sums):
    # Logging stale resource information
    logger.info('=' * 80)
    logger.info(f"Stale resources to remove: {len(stale)}")
    for rtype, rid, _ in stale:
        logger.info(f"  {rtype:{20}}  {rid}")
    logger.info('=' * 80)

    total = len(stale)
    max_len = max(len(rtype) for rtype, _, _ in stale)
    index_width = len(str(total))

    logger.info('Removing stale resources from Canvas')

    # Main logic to remove stale resources
    for index, (rtype, rid, canvas_info) in enumerate(stale, start=1):
        logger.info(f'[{index:>{index_width}}/{total}] {rtype:{max_len}}  {rid}')

        try:
            if canvas_resource := _lookup_stale_canvas_resource(course, rtype, rid, canvas_info):
                canvas_resource.delete()
                md5s.remove((rtype, rid))
        except ResourceDoesNotExist:
            logger.debug(f'{rtype} {rid} not found on Canvas - already removed')
            md5s.remove((rtype, rid))


# =============================================================================
# Logging
# =============================================================================

def log_to_deploy(to_deploy: dict, dryrun=False):
    grouped = defaultdict(int)
    for (rtype, _), _ in to_deploy.keys():
        grouped[rtype] += 1

    logger.info('=' * 80)

    logger.info(f'Resources to deploy: {len(to_deploy)}')
    max_len = max(len(rtype) for rtype in grouped)
    for rtype, count in sorted(grouped.items()):
        logger.info(f'  {rtype:{max_len}}  {count:>3}')

    logger.info('=' * 80)

    if dryrun:
        logger.info('Dry run - no resources deployed')
        return


# =============================================================================
# Main deployment - private helpers
# =============================================================================

def _prepare_deployment_order(resources: dict) -> tuple[dict, list]:
    resource_dependencies = get_dependencies(resources)
    logger.debug(f'Dependency graph: {resource_dependencies}')

    resource_order = linearize_dependencies(resource_dependencies, list(SHELL_DEPLOYERS.keys()))
    logger.debug(f'Linearized dependencies: {resource_order}')

    return resource_dependencies, resource_order


def _deploy_resources(course: Course, to_deploy: dict, md5s: MD5Sums, report: DeploymentReport, dryrun=False):
    log_to_deploy(to_deploy, dryrun=dryrun)

    logger.info('Deploying resources to Canvas')

    resource_objs: dict[tuple[str, str], CanvasObject] = {}
    total = len(to_deploy)
    index_width = len(str(total))
    max_len = max(len(rtype) for (rtype, _), _ in to_deploy.keys())

    for index, ((resource_key, is_shell), (current_md5, resource)) in enumerate(to_deploy.items(), start=1):
        rtype, rid = resource_key

        if (resource_data := resource.get('data')) is not None:
            shell_tag = '(shell) ' if is_shell else ''
            logger.info(f'[{index:>{index_width}}/{total}] {shell_tag}{rtype:{max_len}}  {rid}')

            if is_shell:
                canvas_obj_info, info = deploy_resource(SHELL_DEPLOYERS, course, rtype, resource_data, resource)
                resource['data']['canvas_id'] = canvas_obj_info.get('id') if canvas_obj_info else None
            else:
                resource_data = update_links(md5s, resource_data, resource_objs, resource)
                resource_data = post_process_resource(resource_data)
                canvas_obj_info, info = deploy_resource(DEPLOYERS, course, rtype, resource_data, resource)

            if canvas_obj_info:
                resource_objs[resource_key] = canvas_obj_info
                if url := canvas_obj_info.get('url'):
                    report.add_deployed_content(rtype, rid, url)

            if info:
                report.add_content_to_review(*info)

            md5s[resource_key] = {"checksum": current_md5, "canvas_info": canvas_obj_info}


def _remove_stale_resources(course: Course, resources: dict, md5s: MD5Sums) -> int:
    if stale_resources := get_stale_resources(resources, md5s):
        remove_stale_resources(course, stale_resources, md5s)

    return len(stale_resources) if stale_resources else 0


def _log_completion(actions: list[str], elapsed: float):
    logger.info(
        f"Deployment complete - {' and '.join(actions)} in {elapsed:.1f}s" if actions else
        'No changes detected - nothing to do'
    )


# =============================================================================
# Main entry point
# =============================================================================

def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource],
                     report: DeploymentReport, dryrun=False, cleanup=False):
    resource_dependencies, resource_order = _prepare_deployment_order(resources)

    logger.info('Preparing resources for deployment to Canvas')

    actions = []
    start_time = time.perf_counter()

    with MD5Sums(course) as md5s, TemporaryDirectory() as tmpdir:
        migrate(course, md5s)

        tmpdir = Path(tmpdir)

        predeploy_resources(resources, timezone, tmpdir)

        if to_deploy := identify_modified_or_outdated(resources, resource_order, resource_dependencies, md5s):
            _deploy_resources(course, to_deploy, md5s, report, dryrun=dryrun)
            actions.append(f'{len(to_deploy)} resources deployed')

        if cleanup:
            if removed_count := _remove_stale_resources(course, resources, md5s):
                actions.append(f'{removed_count} stale resources removed')

    _log_completion(actions, time.perf_counter() - start_time)
