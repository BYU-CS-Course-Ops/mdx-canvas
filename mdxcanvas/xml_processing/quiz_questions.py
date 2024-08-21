from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_bool, parse_child_tag_contents, \
    parse_int
from ..util import retrieve_contents


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
        Attribute('points', 1, parse_int, 'points_possible'),
    ]
    question.update(parse_settings(tag, fields))

    # TODO - do we still want to support correct/incorrect comments on the question tag?

    return question


def parse_multiple_true_false_question():
    pass


