from .checksums import MD5Sums
from ..our_logging import get_logger

logger = get_logger()


def migrate(canvas, md5s: MD5Sums):
    """Update the md5 data to match the latest schema"""
    logger.info('Migrating cached data')

    # Titles (0.6.2)
    for (rtype, rid), data in md5s._md5s.items():
        if rtype in ['assignment', 'file', 'module', 'page', 'quiz'] \
                and not data['canvas_info'].get('title'):
            logger.debug(f'Migrating title for {rtype} {rid}')
            canvas_obj = getattr(canvas, f'get_{rtype}')(data['canvas_info']['id'])
            title = (
                canvas_obj.title if hasattr(canvas_obj, 'title') else
                canvas_obj.name if hasattr(canvas_obj, 'name') else
                canvas_obj.display_name
            )
            md5s._md5s[rtype, rid]['canvas_info']['title'] = title

        elif rtype == 'syllabus' and not data.get('title'):
            logger.debug(f'Migrating title for {rtype} {rid}')
            md5s._md5s[rtype, rid]['canvas_info']['title'] = 'Syllabus'
        # TODO 'announcement',
