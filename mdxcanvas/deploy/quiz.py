from canvasapi.course import Course
from canvasapi.quiz import Quiz

from .util import update_group_name_to_id
from ..our_logging import get_logger
from ..resources import QuizInfo

logger = get_logger()


def debug_quiz_creation(canvas_quiz: Quiz, course: Course, data):
    new_settings = {"title": data["title"]}

    for key, value in zip(data.keys(), data.values()):
        new_settings[key] = value
        logger.debug(f"Attempting with {key}: {value}")
        try:
            canvas_quiz = course.create_quiz(quiz=new_settings)
        except Exception as ex:
            logger.exception(f"Failed on key: {key}, value: {value}")
            raise ex
        canvas_quiz.delete()
    return canvas_quiz


def create_quiz(course: Course, data: dict, name: str):
    logger.debug(f"Creating canvas quiz {name}...")
    try:
        canvas_quiz = course.create_quiz(quiz=data)
    except Exception as ex:
        logger.exception(f"Error creating canvas quiz {name}")

        # Perhaps the quiz was partially created, and then the program crashed
        quiz_id = data["canvas_id"]
        if canvas_quiz := course.get_quiz(quiz_id):
            logger.warning(f"Attempting to edit partially created quiz {name}...")
            try:
                canvas_quiz.edit(quiz=data)
            except Exception as ex:
                logger.exception("Failed to edit quiz")
                raise ex
        else:
            logger.error("Quiz was not created")
            logger.error("Attempting to debug quiz creation")
            canvas_quiz = debug_quiz_creation(canvas_quiz, course, data)
    return canvas_quiz


def check_quiz(canvas_quiz, name: str):
    """
    Checks if quiz has submissions and throws a warning with link to quiz.
    """
    if any(canvas_quiz.get_submissions()):
        return f"Quiz {name} has submissions. See {canvas_quiz.html_url} to save quiz."
    return None


def replace_questions(quiz: Quiz, questions: list[dict]):
    """
    Deletes all questions in a quiz, and replaces them with new questions.
    """
    logger.debug(f"Replacing questions ... ")
    for quiz_question in quiz.get_questions():
        quiz_question.delete()
    for question in questions:
        quiz.create_question(question=question)


def deploy_quiz(course: Course, quiz_data: dict) -> tuple[QuizInfo, tuple[str, str] | None]:
    quiz_id = quiz_data["canvas_id"]
    name = quiz_data['title']

    update_group_name_to_id(course, quiz_data)

    info = None
    if quiz_id:
        canvas_quiz = course.get_quiz(quiz_id)
        canvas_quiz: Quiz
        if any(canvas_quiz.get_submissions()):
            # If there are submission, we can't save the new material programmatically,
            #  you have to go in and hit save in the browser
            info = name, canvas_quiz.html_url
        else:
            # unpublish (if needed), push change, republish (if needed)
            is_already_published = canvas_quiz.published
            if is_already_published:
                canvas_quiz.edit(quiz={'published': False})
            quiz_data['published'] = quiz_data.get('published', is_already_published)
        replace_questions(canvas_quiz, quiz_data['questions'])
        canvas_quiz.edit(quiz=quiz_data)
    else:
        canvas_quiz = create_quiz(course, quiz_data, name)
        replace_questions(canvas_quiz, quiz_data['questions'])

    quiz_object_info: QuizInfo = {
        'id': canvas_quiz.id,
        'url': canvas_quiz.html_url,
    }

    return quiz_object_info, info


def deploy_shell_quiz(course: Course, quiz_data: dict) -> tuple[QuizInfo, None]:
    shell_quiz_data = quiz_data.copy()
    shell_quiz_data['questions'] = []
    shell_quiz_data['description'] = "<p>This is a shell page created to break a dependency cycle. The full content will be deployed later.</p>"

    return deploy_quiz(course, shell_quiz_data)
