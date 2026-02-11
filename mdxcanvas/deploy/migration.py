from .. import __version__
from .checksums import MD5Sums
from ..our_logging import get_logger

logger = get_logger()


def _parse_version(v):
    return tuple(int(x) for x in v.split('.'))


def _migrate_titles(course, md5s: MD5Sums):
    for key, data in md5s.items():
        rtype, rid = key

        if rtype in ['assignment', 'file', 'module', 'page', 'quiz'] \
                and not data['canvas_info'].get('title'):
            logger.debug(f'Migrating title for {rtype} {rid}')

            canvas_obj = getattr(course, f'get_{rtype}')(data['canvas_info']['id'])
            title = (
                canvas_obj.title if hasattr(canvas_obj, 'title') else
                canvas_obj.name if hasattr(canvas_obj, 'name') else
                canvas_obj.display_name
            )
            md5s[rtype, rid]['canvas_info']['title'] = title

        elif rtype == 'syllabus' and not data.get('title'):
            logger.debug(f'Migrating title for {rtype} {rid}')
            md5s[rtype, rid]['canvas_info']['title'] = 'Syllabus'


def _migrate_module_and_override_ids(course, md5s: MD5Sums):
    # Module Item -> Module ID map
    item_id_map = {
        module_item.id: module_item.module_id
        for module in course.get_modules()
        for module_item in module.get_module_items()
    }

    # Override -> Assignment ID map
    assignment_id_map = {
        override.id: override.assignment_id
        for assignment in course.get_assignments()
        for override in assignment.get_overrides()
    }

    for key, data in md5s.items():
        rtype, rid = key

        # Module Item -> Module ID
        if rtype == 'module_item' and not data['canvas_info'].get('module_id'):
            logger.debug(f'Migrating module_id for {rtype} {rid}')

            module_item_id = data['canvas_info'].get('id')
            if module_item_id in item_id_map:
                md5s[rtype, rid]['canvas_info']['module_id'] = item_id_map[module_item_id]

        # Override -> Assignment ID
        elif rtype == 'override' and not data['canvas_info'].get('assignment_id'):
            logger.debug(f'Migrating assignment_id for {rtype} {rid}')

            override_id = data['canvas_info'].get('id')
            if override_id in assignment_id_map:
                md5s[rtype, rid]['canvas_info']['assignment_id'] = assignment_id_map[override_id]


def migrate(course, md5s: MD5Sums):
    """Update the md5 data to match the latest schema"""
    logger.info('Checking MDXCanvas version')

    current_version = __version__
    stored_version = md5s.get_mdxcanvas_version()

    # Set version upfront
    md5s.add_mdxcanvas_version(current_version)

    if stored_version == current_version:
        logger.info('MDXCanvas version is up to date, no migration needed')
        return

    if stored_version is None:
        logger.info('No version found — running all migrations')
        stored_ver = (0, 0, 0)
    else:
        logger.info(f'Migrating from {stored_version} to {current_version}')
        stored_ver = _parse_version(stored_version)

    logger.info('Migrating cached data')

    # Titles (0.6.2)
    if stored_ver < (0, 6, 2):
        _migrate_titles(course, md5s)

    # Module Item → Module ID, Override → Assignment ID (0.6.6)
    if stored_ver < (0, 6, 6):
        _migrate_module_and_override_ids(course, md5s)
