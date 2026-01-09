import time
import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import defaultdict
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
from .module import deploy_module, deploy_module_item
from .override import deploy_override
from .page import deploy_page, deploy_shell_page
from .quiz import deploy_quiz, deploy_shell_quiz
from .syllabus import deploy_syllabus
from .zip import deploy_zip, predeploy_zip
from ..deployment_report import DeploymentReport
from ..our_logging import get_logger
from ..resources import CanvasResource, iter_keys

logger = get_logger()

PREDEPLOYERS: dict[str, Callable[[dict, Path], dict]] = {
    'zip': predeploy_zip
}

SHELL_DEPLOYERS = {
    # Current known resources that need shell deployments
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
    'module_item': deploy_module_item,
    'override': deploy_override,
    'page': deploy_page,
    'quiz': deploy_quiz,
    'syllabus': deploy_syllabus,
    'zip': deploy_zip
}


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


def predeploy_resources(resources: dict, timezone: str, tmpdir: Path):
    for resource in resources.values():
        if (data := resource.get('data')) is None:
            continue

        fix_dates(data, timezone, resource)

        rtype = resource['type']
        if predeploy := PREDEPLOYERS.get(rtype):
            logger.debug(f'Predeploying {rtype} {data}')
            resource['data'] = predeploy(data, tmpdir)


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


def deploy_resource(deployers: dict, course: Course, rtype: str, data: dict, resource: CanvasResource):
    if not (deploy := deployers.get(rtype)):
        raise Exception(f"Unsupported resource type {rtype} {resource['id']}\n  in {resource['content_path']}")

    try:
        deployed, info = deploy(course, data)
    except Exception as e:
        raise Exception(
            f"Error deploying {rtype} {resource['id']}\n  {type(e).__name__}: {e}\n  in {resource['content_path']}") from e

    if not deployed:
        raise Exception(f"Deployment returned None for {rtype} {resource['id']}\n  in {resource['content_path']}")

    return deployed, info


def deploy_to_canvas(course: Course, timezone: str, resources: dict[tuple[str, str], CanvasResource],
                     report: DeploymentReport, dryrun=False):
    resource_dependencies = get_dependencies(resources)
    logger.debug(f'Dependency graph: {resource_dependencies}')

    resource_order = linearize_dependencies(resource_dependencies, list(SHELL_DEPLOYERS.keys()))
    logger.debug(f'Linearized dependencies: {resource_order}')

    logger.info('Preparing resources for deployment to Canvas')

    with MD5Sums(course) as md5s, TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        predeploy_resources(resources, timezone, tmpdir)

        to_deploy = identify_modified_or_outdated(resources, resource_order, resource_dependencies, md5s)
        total = len(to_deploy)
        if not total:
            logger.info('No resources to deploy')
            return

        # Summary by type
        grouped = defaultdict(int)
        for (rtype, _), _ in to_deploy.keys():
            grouped[rtype] += 1

        logger.info('=' * 80)

        logger.info(f'Resources to deploy: {total}')
        max_len = max(len(rtype) for rtype in grouped)
        for rtype, count in sorted(grouped.items()):
            logger.info(f'  {rtype:{max_len}}  {count:>3}')

        logger.info('=' * 80)

        if dryrun:
            logger.info('Dry run - no resources deployed')
            return

        logger.info('Deploying resources to Canvas')
        start_time = time.perf_counter()
        resource_objs: dict[tuple[str, str], CanvasObject] = {}
        index_width = len(str(total))
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
                    canvas_obj_info, info = deploy_resource(DEPLOYERS, course, rtype, resource_data, resource)

                if canvas_obj_info:
                    resource_objs[resource_key] = canvas_obj_info
                    if url := canvas_obj_info.get('url'):
                        report.add_deployed_content(rtype, rid, url)

                if info:
                    report.add_content_to_review(*info)

                md5s[resource_key] = {"checksum": current_md5, "canvas_info": canvas_obj_info}

        elapsed = time.perf_counter() - start_time
        logger.info(f'Deployment complete - {total} resources in {elapsed:.1f}s')
