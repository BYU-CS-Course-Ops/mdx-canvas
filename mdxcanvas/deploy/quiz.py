from canvasapi.course import Course
from canvasapi.quiz import QuizQuestion

from .util import update_group_name_to_id
from ..resources import QuizInfo, QuizQuestionInfo, QuizQuestionOrderInfo


def get_quiz_question(course: Course, quiz_id: int, question_id: int) -> QuizQuestion | None:
    """Lookup a quiz question for stale resource handling."""
    if canvas_quiz := course.get_quiz(quiz_id):
        return canvas_quiz.get_question(question_id)
    return None


def get_quiz_review_info(canvas_quiz) -> tuple[str, str] | None:
    if any(canvas_quiz.get_submissions()):
        return canvas_quiz.title, canvas_quiz.html_url
    return None


def unpublish_quiz_for_edit(canvas_quiz) -> bool:
    was_published = canvas_quiz.published
    if was_published:
        canvas_quiz.edit(quiz={'published': False})
    return was_published


def republish_quiz_after_edit(canvas_quiz, was_published: bool):
    if was_published:
        canvas_quiz.edit(quiz={'published': True})


def deploy_quiz(course: Course, quiz_data: dict) -> tuple[QuizInfo, tuple[str, str] | None]:
    """Deploy quiz settings/metadata only. Questions are deployed separately."""
    quiz_id = quiz_data["canvas_id"]

    update_group_name_to_id(course, quiz_data)

    info = None
    if quiz_id:
        # Updating existing quiz
        canvas_quiz = course.get_quiz(quiz_id)
        info = get_quiz_review_info(canvas_quiz)

        was_published = False

        if info is None:
            # No submissions - safe to unpublish, edit, republish
            was_published = unpublish_quiz_for_edit(canvas_quiz)
            quiz_data['published'] = quiz_data.get('published', was_published)

        # else: has submissions - edit anyway, user must manually save in browser
        canvas_quiz.edit(quiz=quiz_data)

        if info is None:
            # No submissions - republish if needed
            republish_quiz_after_edit(canvas_quiz, was_published)
    else:
        # Creating new quiz
        canvas_quiz = course.create_quiz(quiz=quiz_data)

    return QuizInfo(
        id=canvas_quiz.id,
        title=canvas_quiz.title,
        uri=f'/courses/{course.id}/quizzes/{canvas_quiz.id}',
        url=canvas_quiz.html_url if hasattr(canvas_quiz, 'html_url') else None
    ), info


def deploy_quiz_question(course: Course, quiz_question_data: dict) -> tuple[QuizQuestionInfo, tuple[str, str] | None]:
    if not (canvas_quiz := course.get_quiz(quiz_question_data['quiz_id'])):
        raise ValueError(f'Unable to find quiz {quiz_question_data["quiz_id"]}')

    info = None
    if quiz_question_data['canvas_id'] is not None and (
            quiz_question := canvas_quiz.get_question(quiz_question_data['canvas_id'])):
        # Updating existing question
        info = get_quiz_review_info(canvas_quiz)

        was_published = False

        if info is None:
            # No submissions - safe to unpublish, edit, republish
            was_published = unpublish_quiz_for_edit(canvas_quiz)

        # else: has submissions - edit anyway, user must manually save in browser
        quiz_question.edit(question=quiz_question_data)

        if info is None:
            # No submissions - republish if needed
            republish_quiz_after_edit(canvas_quiz, was_published)
    else:
        # Creating new question
        quiz_question = canvas_quiz.create_question(question=quiz_question_data)

    return QuizQuestionInfo(
        id=quiz_question.id,
        quiz_id=canvas_quiz.id,
        uri=f'/courses/{course.id}/quizzes/{canvas_quiz.id}',
        url=canvas_quiz.html_url if hasattr(canvas_quiz, 'html_url') else None
    ), info


def deploy_quiz_question_order(course: Course, order_data: dict) -> tuple[QuizQuestionOrderInfo, tuple[str, str] | None]:
    """
    Reorder quiz questions using Canvas API.
    NOTE: No CanvasAPI wrapper method exists for this endpoint.

    Args:
        course: Canvas course object
        order_data: Dict with quiz_id and order list
    """
    quiz_id = order_data['quiz_id']
    order_items = order_data['order']

    canvas_quiz = course.get_quiz(quiz_id)

    info = get_quiz_review_info(canvas_quiz)

    was_published = False

    if info is None:
        # No submissions - safe to unpublish, reorder, republish
        was_published = unpublish_quiz_for_edit(canvas_quiz)
    # else: has submissions - reorder anyway, user must manually save in browser

    # Canvas API expects order as repeated form fields: order[][id]=1&order[][type]=question
    # Build the _kwargs format that canvasapi's request method accepts
    order_params = []
    for item in order_items:
        order_params.append(('order[][id]', item['id']))
        order_params.append(('order[][type]', item['type']))

    course._requester.request(
        'POST',
        f'courses/{course.id}/quizzes/{quiz_id}/reorder',
        _kwargs=order_params
    )

    if info is None:
        # No submissions - republish if needed
        republish_quiz_after_edit(canvas_quiz, was_published)

    return QuizQuestionOrderInfo(
        id=f'{quiz_id}_order',
        quiz_id=quiz_id,
        uri=f'/courses/{course.id}/quizzes/{quiz_id}',
        url=canvas_quiz.html_url if hasattr(canvas_quiz, 'html_url') else None
    ), info


def deploy_shell_quiz(course: Course, quiz_data: dict) -> tuple[QuizInfo, tuple[str, str] | None]:
    shell_quiz_data = quiz_data.copy()
    shell_quiz_data['description'] = "<p>Shell quiz for dependency cycle.</p>"
    return deploy_quiz(course, shell_quiz_data)
