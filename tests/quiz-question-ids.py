import json
import os
from pathlib import Path
from canvasapi.quiz import Quiz

from mdxcanvas.main import load_config, get_course


if __name__ == '__main__':
    course_info_path = Path('/Users/robbykapua/Documents/GitHub/beanlab-dev/mdx-canvas/scratch/testing_course_info.json')
    course_info = load_config(course_info_path)

    canvas_api_token = os.environ.get('CANVAS_API_TOKEN')

    course = get_course(canvas_api_token, course_info['CANVAS_API_URL'], course_info['CANVAS_COURSE_ID'])

    quiz_id = 598553

    quiz: Quiz = course.get_quiz(quiz_id)

    print(f"Link to Quiz: {quiz.html_url}")

    quiz_questions = quiz.get_questions()

    for question in quiz_questions:
        print(json.dumps(question.__dict__['position'], indent=4, default=str))
