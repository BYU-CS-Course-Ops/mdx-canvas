import logging

from canvasapi.course import Course
from canvasapi.quiz import Quiz

from .util import get_canvas_object, update_group_name_to_id, ResourceNotFoundException


def get_quiz(course: Course, title: str) -> Quiz:
    return get_canvas_object(course.get_quizzes, "title", title)


def debug_quiz_creation(canvas_quiz: Quiz, course: Course, data):
    new_settings = {"title": data["title"]}

    for key, value in zip(data.keys(), data.values()):
        new_settings[key] = value
        logging.debug(f"Attempting with {key}: {value}")
        try:
            canvas_quiz = course.create_quiz(quiz=new_settings)
        except Exception as ex:
            logging.exception(f"Failed on key: {key}, value: {value}")
            raise ex
        canvas_quiz.delete()
    return canvas_quiz


def create_quiz(course: Course, data: dict, name: str):
    logging.debug(f"Creating canvas quiz {name}...")
    try:
        canvas_quiz = course.create_quiz(quiz=data)
    except Exception as ex:
        logging.exception(f"Error creating canvas quiz {name}")

        # Perhaps the quiz was partially created, and then the program crashed
        if canvas_quiz := get_quiz(course, name):
            logging.warning(f"Attempting to edit partially created quiz {name}...")
            try:
                canvas_quiz.edit(quiz=data)
            except Exception as ex:
                logging.exception("Failed to edit quiz")
                raise ex
        else:
            logging.error("Quiz was not created")
            logging.error("Attempting to debug quiz creation")
            canvas_quiz = debug_quiz_creation(canvas_quiz, course, data)
    return canvas_quiz


def replace_questions(quiz: Quiz, questions: list[dict]):
    """
    Deletes all questions in a quiz, and replaces them with new questions.
    """
    logging.debug(f"Replacing questions ... ")
    for quiz_question in quiz.get_questions():
        quiz_question.delete()
    for question in questions:
        quiz.create_question(question=question)


def deploy_quiz(course: Course, quiz_data: dict) -> Quiz:
    name = quiz_data['title']

    update_group_name_to_id(course, quiz_data)

    if canvas_quiz := get_quiz(course, name):
        canvas_quiz: Quiz
        canvas_quiz.edit(quiz=quiz_data)
    else:
        canvas_quiz = create_quiz(course, quiz_data, name)

    replace_questions(canvas_quiz, quiz_data['questions'])
    canvas_quiz.edit()

    return canvas_quiz


def lookup_quiz(course: Course, quiz_name: str) -> Quiz:
    canvas_quiz = get_quiz(course, quiz_name)
    if not canvas_quiz:
        raise ResourceNotFoundException(f'Quiz {quiz_name} not found')
    return canvas_quiz
