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

    # Quiz Question -> Quiz ID map (0.6.10)
    quiz_id_map = {
        f"{question.id}|{i}": question.quiz_id
        for quiz in course.get_quizzes()
        for i, question in enumerate(quiz.get_questions())
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

    # Quiz Question -> Quiz ID (0.6.10)
    # Non-trivial task as we are not updating existing resources but adding new ones
    #
    # TODO: This may be unnecessary the point in migrating is to prevent re-deployment issues
    #  however since we are introducing new resources even if we add them to the md5s cache
    #  they will still be deployed since they have no checksum yet.
    #
    # for key, quiz_id in quiz_id_map.items():
    #     question_id, pos = key.split('|', 1)
    #
    #     if quiz_rid:=md5s._md5s.get_rid(quiz_id):
    #
    #         # TODO: Need a better way to check if we already have this resource
    #         if not ('quiz_question', f'{quiz_rid}|') in md5s._md5s.items():
    #
    #             logger.debug(f'Migrating quiz_id for quiz_question {question_id}')
    #
    #             quiz_data = md5s._md5s.get_canvas_info(('quiz', quiz_rid))
    #
    #             # TODO: Edge case: How to handle multiple-tf questions? Since we view them as
    #             #  one question but they are multiple questions in Canvas and we need to assign
    #             #  its parts sub positions (i.e. q1_1, q1_2, etc)
    #             md5s._md5s['quiz_question', f'{quiz_rid}|q{pos}']['canvas_info'] = {
    #                 'id': question_id,
    #                 'quiz_id': quiz_id,
    #                 'uri': quiz_data['uri'],
    #                 'url': quiz_data['url']
    #             }
    #
    #             md5s._md5s['quiz_question_order', f'{quiz_rid}|order']['md5'] = {
    #                 'quiz_id': quiz_id,
    #                 'uri': quiz_data['uri'],
    #                 'url': quiz_data['url']
    #             }
    #
