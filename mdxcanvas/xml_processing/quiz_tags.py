from .attributes import Attribute, parse_int, parse_bool, parse_date, parse_settings, parse_child_tag_contents, \
    retrieve_contents
from ..resources import ResourceManager, CanvasResource
from bs4 import Tag


def parse_text_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'text_only_question',
    }
    return question


def parse_true_false_question(tag: Tag):
    """
    <question type='true-false' answer='true'>
    The earth is round
    </question>

    <question type='true-false' answer='false'>
    The earth is **flat**
    </question>
    """
    correct_response = parse_bool(tag.get('answer', 'false'))

    question = {
        "question_text": retrieve_contents(tag),
        "question_type": 'true_false_question',
        "correct_comments": parse_child_tag_contents(tag, 'correct-comments'),
        "incorrect_comments": parse_child_tag_contents(tag, 'incorrect-comments'),
        "answers": [
            {
                "answer_text": "True",
                "answer_weight": 100 if correct_response else 0
            },
            {
                "answer_text": "False",
                "answer_weight": 0 if correct_response else 100
            }
        ]
    }

    fields = [
        Attribute('points', 1, parse_bool, 'points_possible'),
    ]
    question.update(parse_settings(tag, fields))

    # TODO - do we still want to support correct/incorrect comments on the question tag?

    return question


def parse_multiple_true_false_question():
    pass


class QuizTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources
        self.question_types = {
            'text': parse_text_question,
            'true-false': parse_true_false_question
        }

    def __call__(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
            "name": quiz_tag["title"],
            "questions": [],
            "resources": []
        }
        quiz.update(self._parse_quiz_settings(quiz_tag))

        for tag in quiz_tag.children:
            if not isinstance(tag, Tag):
                continue  # Top-level content is not supported in a quiz tag

            if tag.name == "questions":
                questions = self._parse_questions(tag)
                quiz["questions"].extend(questions)

            elif tag.name == "description":
                quiz["description"] = retrieve_contents(tag)

        info = CanvasResource(
            type='quiz',
            name=quiz['name'],
            data=quiz
        )
        self._resources.add_resource(info)

    def _parse_quiz_settings(self, settings_tag):
        fields = [
            Attribute('title', required=True),
            Attribute('quiz_type', 'assignment'),
            Attribute('assignment_group'),
            Attribute('time_limit', parser=parse_int),
            Attribute('shuffle_answers', False, parse_bool),
            Attribute('hide_results'),  # TODO - should be boolean?
            Attribute('show_correct_answers', True, parse_bool),
            Attribute('show_correct_answers_last_attempt', False, parse_bool),
            Attribute('show_correct_answers_at', parser=parse_date),
            Attribute('hide_correct_answers_at', parser=parse_date),
            Attribute('allowed_attempts', -1, parse_int),
            Attribute('scoring_policy', 'keep_highest'),
            Attribute('one_question_at_a_time', False, parse_bool),
            Attribute('cant_go_back', False, parse_bool),
            Attribute('available_from', parser=parse_date, new_name='unlock_at'),
            Attribute('available_to', parser=parse_date, new_name='lock_at'),
            Attribute('due_at', parser=parse_date),
            Attribute('access_code'),
            Attribute('published', False, parse_bool),
            Attribute('one_time_results', False, parse_bool)
        ]

        return parse_settings(settings_tag, fields)

    def _parse_questions(self, questions_tag: Tag):
        questions = []
        for question in questions_tag.findAll('question', recursive=False):
            # TODO - add validation for "type" field (present and supported)
            parse_tag = self.question_types[question["type"]]
            questions.append(parse_tag(question))
        return questions
