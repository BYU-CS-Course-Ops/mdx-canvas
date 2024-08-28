from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_bool, parse_child_tag_contents, \
    parse_int, parse_children_tag_contents
from ..util import retrieve_contents

NO_POINTS = 0
FULL_POINTS = 100


def parse_text_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'text_only_question',
    }
    return question


def parse_true_false_question(tag: Tag):
    """
    <question type='true-false' answer='true' points_possible=2>
    The earth orbits the sun
    </question>

    <question type='true-false' answer='false'>
    The earth is **flat**

    <correct-comments>
    A nationwide survey in 2022 by researchers at the University of New Hampshire found that
    10% of U.S. adults believed the earth was flat.
    </correct_comments>

    <incorrect-comments>
    Regular folks who like math and stars rely on the curvature on the earth to track the motion
    of heavenly bodies.
    </question>
    """
    fields = [
        Attribute('points', 1, parse_int, 'points_possible'),
        Attribute('correct-comments'),
        Attribute('incorrect-comments'),
        Attribute('answer', required=True, parser=parse_bool, default=False),
        Attribute('type', recognize_and_discard=True)
    ]
    question = parse_settings(tag, fields)

    question.update({
        "question_text": retrieve_contents(tag),
        "question_type": 'true_false_question',
        "answers": [
            {
                "answer_text": "True",
                "answer_weight": FULL_POINTS if question["answer"] is True else NO_POINTS
            },
            {
                "answer_text": "False",
                "answer_weight": FULL_POINTS if question["answer"] is False else NO_POINTS
            }
        ]
    })

    # TODO - do we still want to support correct/incorrect comments on the question tag?

    return question


def parse_multiple_choice_question(tag: Tag):
    """
    <question type='multiple-choice'>
    5 + 5 =
    <correct> 10 </correct>
    <incorrect> 11 </incorrect>
    <incorrect> 9 </incorrect>
    <incorrect> 8 </incorrect>
    </question>
    """

    corrects = parse_children_tag_contents(tag, 'correct')
    if len(corrects) != 1:
        raise ValueError("Multiple choice questions must have exactly one correct answer!")
    return _parse_multiple_option_question('multiple_choice_question', tag)


def parse_multiple_answers_question(tag: Tag):
    """
    <question type='multiple-answers'>
    Which of the following are prime numbers?
    <correct> 2 </correct>
    <correct> 3 </correct>
    <incorrect> 4 </incorrect>
    <correct> 5 </correct>
    <incorrect> 6 </incorrect>
    </question>
    """
    return _parse_multiple_option_question('multiple_answers_question', tag)


def _parse_multiple_option_question(question_type, tag):
    corrects = parse_children_tag_contents(tag, 'correct')
    answers = parse_children_tag_contents(tag, lambda x: x in ['correct', 'incorrect'])
    question = {
        "question_text": retrieve_contents(tag),
        "question_type": question_type,
        "answers": [
            {
                "answer_html": answer,
                "answer_weight": FULL_POINTS if answer in corrects else NO_POINTS
            } for answer in answers
        ]
    }
    fields = [
        Attribute('points', 1, parse_int, 'points_possible'),
        Attribute('correct-comments'),
        Attribute('incorrect-comments')
    ]
    question.update(parse_settings(tag, fields))
    return question


def parse_matching_question(tag: Tag):
    """
    <question type='matching'>
    Match the following:
    <pair>
    <left> 1 </left>
    <right> A </right>
    </pair>
    <pair>
    <left> 2 </left>
    <right> B </right>
    </pair>
    <pair>
    <left> 3 </left>
    <right> C </right>
    </pair>
    <distractor> D </distractor>
    <distractor> E </distractor>
    <correct-comments>Good job!</correct-comments>
    </question>
    """
    pairs = tag.select('pair')
    matches = []
    for pair in pairs:
        answer_left = parse_child_tag_contents(pair, 'left')
        answer_right = parse_child_tag_contents(pair, 'right')
        matches.append((answer_left, answer_right))

    distractors = parse_children_tag_contents(tag, 'distractor')

    question = {
        "question_text": retrieve_contents(tag),
        "question_type": 'matching_question',
        "points_possible": parse_int(tag.get('points') or len(matches)),
        "correct_comments": parse_child_tag_contents(tag, 'correct-comments'),
        "incorrect_comments": parse_child_tag_contents(tag, 'incorrect-comments'),
        "answers": [
            {
                "answer_match_left": answer_left,
                "answer_match_right": answer_right,
                "answer_weight": FULL_POINTS
            } for answer_left, answer_right in matches
        ],
        "matching_answer_incorrect_matches": '\n'.join(distractors)
    }
    return question


def parse_multiple_true_false_question():
    """
    <question type='multiple-tf'>
    Which of the following matrices are invertible?

    A: [[1, 0], [0, 1]]
    B: [[1, 0], [1, 0]]
    C: [[1, 1], [1, 1]]
    D: [[0, 0], [0, 0]]

    <correct> A </correct>
    <incorrect> B </incorrect>
    <incorrect> C </incorrect>
    <incorrect> D </incorrect>
    """
    pass




