from .checksums import MD5Sums
from ..our_logging import get_logger

logger = get_logger()


def migrate(course, md5s: MD5Sums):
    """Update the md5 data to match the latest schema"""
    logger.info('Migrating cached data')

    # Module Item -> Module ID map (0.6.6)
    item_id_map = {
        module_item.id: module_item.module_id
        for module in course.get_modules()
        for module_item in module.get_module_items()
    }

    # Override -> Assignment ID map (0.6.6)
    assignment_id_map = {
        override.id: override.assignment_id
        for assignment in course.get_assignments()
        for override in assignment.get_overrides()
    }

    for (rtype, rid), data in md5s._md5s.items():
        # Titles (0.6.2)
        if rtype in ['assignment', 'file', 'module', 'page', 'quiz'] \
                and not data['canvas_info'].get('title'):
            logger.debug(f'Migrating title for {rtype} {rid}')

            canvas_obj = getattr(course, f'get_{rtype}')(data['canvas_info']['id'])
            title = (
                canvas_obj.title if hasattr(canvas_obj, 'title') else
                canvas_obj.name if hasattr(canvas_obj, 'name') else
                canvas_obj.display_name
            )
            md5s._md5s[rtype, rid]['canvas_info']['title'] = title

        elif rtype == 'syllabus' and not data.get('title'):

            logger.debug(f'Migrating title for {rtype} {rid}')
            md5s._md5s[rtype, rid]['canvas_info']['title'] = 'Syllabus'

        # Module Item -> Module ID (0.6.6)
        elif rtype == 'module_item' and not data['canvas_info'].get('module_id'):
            logger.debug(f'Migrating module_id for {rtype} {rid}')

            module_item_id = data['canvas_info'].get('id')
            if module_item_id in item_id_map:
                md5s._md5s[rtype, rid]['canvas_info']['module_id'] = item_id_map[module_item_id]

        # Override -> Assignment ID (0.6.6)
        elif rtype == 'override' and not data['canvas_info'].get('assignment_id'):
            logger.debug(f'Migrating assignment_id for {rtype} {rid}')

            override_id = data['canvas_info'].get('id')
            if override_id in assignment_id_map:
                md5s._md5s[rtype, rid]['canvas_info']['assignment_id'] = assignment_id_map[override_id]
