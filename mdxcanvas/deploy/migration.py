from collections import defaultdict

from canvasapi.quiz import Quiz, QuizQuestion

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


def _migrate_prune_stale_questions(course, md5s: MD5Sums):
    # Map each tracked quiz to its live questions on Canvas
    tracked_quizzes = {
        (quiz_id := data['canvas_info']['id']): [q.id for q in course.get_quiz(quiz_id).get_questions()]
        for key, data in md5s.items()
        if key[0] == 'quiz' and 'id' in data.get('canvas_info', {})
    }

    # Collect question IDs that should be kept (present in md5s)
    questions_to_keep = defaultdict(set)
    for (rtype, _), data in md5s.items():
        if rtype == 'quiz_question':
            quiz_id = data['canvas_info'].get('quiz_id')
            question_id = data['canvas_info'].get('id')
            if quiz_id in tracked_quizzes and question_id in tracked_quizzes[quiz_id]:
                questions_to_keep[quiz_id].add(question_id)

    # Delete questions on Canvas that are no longer in md5s
    for quiz_id, question_ids in tracked_quizzes.items():
        stale_ids = [q_id for q_id in question_ids if q_id not in questions_to_keep[quiz_id]]
        if not stale_ids:
            continue
        quiz: Quiz = course.get_quiz(quiz_id)
        for question_id in stale_ids:
            logger.debug(f'Pruning stale question {question_id} from quiz {quiz_id}')
            try:
                quiz.get_question(question_id).delete()
            except Exception:
                logger.debug(f'Failed to delete question {question_id} from quiz {quiz_id}')


def migrate(course, md5s: MD5Sums):
    """Update the md5 data to match the latest schema"""
    logger.info('Checking MDXCanvas version')

    current_version = __version__
    stored_version = md5s.get_mdxcanvas_version()

    if stored_version == current_version:
        logger.info('MDXCanvas version is up to date, no migration needed')
        return

    if stored_version is None:
        logger.info('No version found — running all migrations')
        stored_ver = (0, 0, 0)
    elif stored_version > current_version:
        logger.warning(f'MDXCanvas version {stored_version} is newer than current version {current_version}. '
                       f'No migrations will be run to avoid potential data loss, but unexpected behavior may occur. '
                       f'Consider updating MDXCanvas to the latest version.')
        return
    else:
        logger.info(f'Migrating from {stored_version} to {current_version}')
        stored_ver = _parse_version(stored_version)

    logger.info('Migrating cached data')

    # Titles (0.6.2)
    if stored_ver < (0, 6, 2):
        logger.info('Adding titles to cached data')
        _migrate_titles(course, md5s)

    # Module Item → Module ID, Override → Assignment ID (0.6.6)
    if stored_ver < (0, 6, 6):
        logger.info('Migrating module and override IDs')
        _migrate_module_and_override_ids(course, md5s)

    # Prune stale quiz questions (0.6.15)
    if stored_ver < (0, 6, 15):
        logger.info('Pruning stale quiz questions')
        _migrate_prune_stale_questions(course, md5s)

    # Now that migration is finished, set the version we are using
    md5s.add_mdxcanvas_version(current_version)
