from canvasapi.course import Course
from canvasapi.quiz import QuizQuestion

from .util import update_group_name_to_id
from ..resources import QuizInfo, QuizQuestionInfo


def deploy_quiz_question(course: Course, quiz_question_data: dict) -> QuizQuestionInfo:
    if not (canvas_quiz := course.get_quiz(quiz_question_data['quiz_id'])):
        raise ValueError(f'Unable to find quiz {quiz_question_data["quiz_id"]}')

    if quiz_question_data['canvas_id'] is not None and (
            quiz_question := canvas_quiz.get_question(quiz_question_data['canvas_id'])):
        quiz_question.edit(question=quiz_question_data)
    else:
        quiz_question = canvas_quiz.create_question(question=quiz_question_data)

    return QuizQuestionInfo(
        id=quiz_question.id,
        quiz_id=canvas_quiz.id,
        uri=f'/courses/{course.id}/quizzes/{canvas_quiz.id}',
        url=canvas_quiz.html_url if hasattr(canvas_quiz, 'html_url') else None,
        position=quiz_question_data.get('position', 0)
    )


def deploy_quiz(course: Course, quiz_data: dict) -> QuizInfo:
    """Deploy quiz settings/metadata only. Questions are deployed separately."""
    quiz_id = quiz_data["canvas_id"]

    update_group_name_to_id(course, quiz_data)

    if quiz_id:
        canvas_quiz = course.get_quiz(quiz_id)
        if 'published' not in quiz_data:
            quiz_data['published'] = canvas_quiz.published
        canvas_quiz.edit(quiz=quiz_data)
    else:
        canvas_quiz = course.create_quiz(quiz=quiz_data)

    return QuizInfo(
        id=canvas_quiz.id,
        title=canvas_quiz.title,
        uri=f'/courses/{course.id}/quizzes/{canvas_quiz.id}',
        url=canvas_quiz.html_url if hasattr(canvas_quiz, 'html_url') else None
    )


def deploy_shell_quiz(course: Course, quiz_data: dict) -> QuizInfo:
    shell_quiz_data = quiz_data.copy()
    shell_quiz_data['description'] = "<p>Shell quiz for dependency cycle.</p>"
    return deploy_quiz(course, shell_quiz_data)


def get_quiz_question(course: Course, quiz_id: int, question_id: int) -> QuizQuestion | None:
    """Lookup a quiz question for stale resource handling."""
    if canvas_quiz := course.get_quiz(quiz_id):
        return canvas_quiz.get_question(question_id)
    return None


def reorder_quiz_questions(course: Course, quiz_id: int, question_order: list[dict]):
    """
    Reorder quiz questions using Canvas API.
    NOTE: No CanvasAPI wrapper method exists for this endpoint.

    Args:
        course: Canvas course object
        quiz_id: Canvas quiz ID
        question_order: List of dicts with 'id' and 'type' keys
    """
    # Canvas API expects order as repeated form fields: order[][id]=1&order[][type]=question
    # Build the _kwargs format that canvasapi's request method accepts
    order_params = []
    for item in question_order:
        order_params.append(('order[][id]', item['id']))
        order_params.append(('order[][type]', item['type']))

    course._requester.request(
        'POST',
        f'courses/{course.id}/quizzes/{quiz_id}/reorder',
        _kwargs=order_params
    )
