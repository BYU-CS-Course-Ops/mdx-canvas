import json
import re
import sys

from pathlib import Path
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.quiz import Quiz
from canvasapi.submission import Submission
from canvasapi import Canvas
from canvas_creator import update_quiz
import os

this_directory = Path(__file__).parent


def get_canvas_from_secrets():
    """
    Returns a Canvas object for the given API URL and API token.

    :return: Canvas: A Canvas object.
    """
    with open(this_directory / "secrets.env") as f:
        secrets = dict(map(lambda line: tuple(line.strip().split("=")), f))
    api_token = secrets["CANVAS_API_TOKEN"]
    api_url: str = "https://byu.instructure.com/"
    canvas = Canvas(api_url, api_token)
    return canvas


def get_course_object(api_url: str, api_token: str, canvas_course_id: int):
    """
    Returns a Canvas Course object for the given API URL, API token, and course ID.

    :param api_url: str: The URL for the Canvas API.
    :param api_token: str: The authentication token for the Canvas API.
    :param canvas_course_id: int: The ID of the Canvas course.
    :return: Course: A Canvas Course object.
    """
    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(canvas_course_id)
    return course


def get_assignment_object(course: Course, assignment_name):
    """
    Returns the Canvas Assignment object that corresponds to the given name.

    :param course: Course: The Canvas Course object.
    :param assignment_name: str: The name of the assignment to match.
    :return: Assignment | None: The Assignment object from Canvas, or None if not found.
    """
    # student = course.get_user(student_id)
    assignment: Assignment = get_canvas_assignment(course, assignment_name)

    if not assignment:
        print(f"Assignment {assignment_name} not found")
        return None
    return assignment


def update_grade_by_submission(submission: Submission, score: float):
    """
        Updates the score for a submission in Canvas.

        :param submission: Submission: The Canvas Submission object.
        :param score: float: The score to assign to the student.
        :return: None
        """
    submission.edit(submission={"posted_grade": score})


def get_gradescope_info(metadata: dict) -> tuple[int, str]:
    """
    Extracts the student ID and the assignment name from the given metadata dictionary.

    :param metadata: dict: The metadata dictionary to extract information from.
    :return: tuple[int, str]: A tuple containing the student ID and assignment name.
    """
    student_id: int = metadata["users"][0]["sid"]
    assignment_name: str = metadata["assignment"]["title"]
    return student_id, assignment_name


def get_canvas_assignment(course: Course, gs_name: str) -> Assignment | None:
    """
    Returns the Canvas Assignment object that corresponds to the given Gradescope
    assignment name. Returns None if the assignment is not found.

    :param course: Course: The Canvas Course object.
    :param gs_name: str: The name of the Gradescope assignment to match.
    :return: Assignment | None: The Assignment object from Canvas, or None if not found.
    """
    name_ids: dict[str, int] = {a.name: int(a.id) for a in course.get_assignments()}
    # Match 1a, 1, 2b
    quantifier = re.search(r"\b\d+\w?\b", gs_name)
    if quantifier:
        # Look for the quantifier in the canvas assignments
        for name in name_ids:
            if quantifier.group(0) in name:
                return course.get_assignment(name_ids[name])
    else:
        print("Quantifier not found")
    return None


def get_email_to_canvas_ids(course: Course):
    for user in course.get_users(enrollment_type="student"):
        if hasattr(user, "email"):
            print(user.email, user.id)
    return {user.email: int(user.id) for user in course.get_users() if hasattr(user, "email")}


def get_course_via_prompt(canvas: Canvas):
    # Prompts for course to update based on personal course list
    # No need for course_info.txt :)
    courses = [c for c in canvas.get_courses(include=['concluded']) if not c.concluded]

    for i, course in enumerate(courses):
        print(f"{i}: {course}")
    response = input("Choose Class: ")
    return canvas.get_course(courses[int(response)].id)


def get_object_via_prompt(canvas: Canvas):
    courses = [c for c in canvas.get_courses(include=['concluded']) if not c.concluded]

    for i, course in enumerate(courses):
        print(f"{i}: {course}")
    response = input("Choose Class: ")
    course_id = courses[int(response)].id
    course = canvas.get_course(course_id)
    response = input(f"Course Selected: {course.name}\n"
                     f"Enter for course, a for assignments, q for quizzes, d for dir: ")
    if response == "a":
        assignment = get_assignment_via_prompt(course)
        response = input(f"Assignment Selected: {assignment.name}\n"
                         f"Enter for assignment, s for submissions, d for dir: ")
        if response == "":
            return assignment
        elif response == "s":
            submission = get_submission_via_prompt(assignment)
            response = input(f"Submission Selected: {submission.user_id}\n"
                             f"Enter to stop, d for dir: ")
            if response == "":
                return submission
            else:
                return print_dir(submission)
        else:
            return print_dir(assignment)

    elif response == "q":
        quiz = get_quiz_via_prompt(course)
        response = input(f"Quiz Selected: {quiz.title}\n"
                         f"Enter for quiz, q for questions, d for dir: ")
        if response == "q":
            question = get_quiz_question_via_prompt(quiz)
            response = input(f"Question Selected: {question.question_text}\n"
                             f"Enter for question, d for dir: ")
            if response == "d":
                return print_dir(question)
            else:
                return question
        elif response == "d":
            return print_dir(quiz)
        else:
            return quiz
    elif response == "d":
        return print_dir(course)
    else:
        return course


def print_dir(object):
    for att in dir(object):
        print(f"{att}: {getattr(object, att)}")
    return object


def get_assignment_via_prompt(course):
    assignments = [a for a in course.get_assignments()]
    for i, assignment in enumerate(assignments):
        print(f"{i}: {assignment}")
    response = input("Choose Assignment: ")
    assignment_id = assignments[int(response)].id
    return course.get_assignment(assignment_id)


def get_submission_via_prompt(assignment):
    submissions = [s for s in assignment.get_submissions()]
    for i, submission in enumerate(submissions):
        print(f"{i}: {submission}")
    response = input("Choose Submission: ")
    submission_id = submissions[int(response)].id
    return assignment.get_submission(submission_id)


def get_quiz_via_prompt(course):
    quizzes = [q for q in course.get_quizzes()]
    for i, quiz in enumerate(quizzes):
        print(f"{i}: {quiz}")
    response = input("Choose Quiz: ")
    quiz_id = quizzes[int(response)].id
    return course.get_quiz(quiz_id)


def get_quiz_question_via_prompt(quiz):
    quiz_questions = [q for q in quiz.get_questions()]
    for i, question in enumerate(quiz_questions):
        print(f"{i}: {question}")
    response = input("Choose Question: ")
    question_id = quiz_questions[int(response)].id
    return quiz.get_question(question_id)


def update_canvas(canvas_course_id: int):
    """
    Updates the grade for a single student in Canvas based on the metadata provided
    in the submission_metadata.json file. Requires a Canvas API URL, API token, and
    course ID to be specified as command-line arguments.

    :param canvas_course_id: int: The ID of the Canvas course.
    :return: None
    """
    # Load the metadata json into a dictionary
    try:
        with open('submission_metadata.json') as f:
            metadata: dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load submission metadata: {e}")
        sys.exit(1)

    student_id, assignment_name = get_gradescope_info(metadata)

    # Get score for submission
    score: float = 3

    canvas = get_canvas_from_secrets()
    course = get_course_via_prompt(canvas)

    assignment = get_assignment_object(course, assignment_name)
    submission = assignment.get_submission(student_id)

    try:
        update_grade_by_submission(submission, score)
        print(f"Successfully updated grade for student {student_id} to {score}")
    except Exception as e:
        print(f"Failed to update grade for student {student_id}: {e}")
        return


def prompt_for_update_type() -> int:
    option = int(input("Input the number of full updated assignments to ignore before stopping,\n"
                       "or type \"0\" to update all assignments: "))
    return option


if __name__ == '__main__':
    try:
        update_canvas(int(sys.argv[1]))
    except (IndexError, ValueError):
        print("Usage: python update_canvas.py [integer canvas_course_id]")
        sys.exit(1)


def get_canvas_id_to_sorted_name(course):
    canvas_id_to_sorted_name = {}
    for user in course.get_users(enrollment_type=["student", "student_view"]):
        if hasattr(user, "sortable_name"):
            canvas_id_to_sorted_name[user.id] = user.sortable_name
    return canvas_id_to_sorted_name


def get_quiz(course: Course, title: str):
    quizzes = course.get_quizzes()
    for quiz in quizzes:
        if quiz.title == title:
            return quiz

    return None

def get_quiz_path():
    path = Path(__file__).parent / "markdown-quiz-files"
    while os.path.isdir(path):
        files = os.listdir(path)
        for i, f in enumerate(files):
            print(f"{i}: {f}")
        index = input("Select file: ")
        try:
            index = int(index)
            path = path / files[index]
        except Exception:
            print(f"Enter a number in the range {len(files)}")
    return path
