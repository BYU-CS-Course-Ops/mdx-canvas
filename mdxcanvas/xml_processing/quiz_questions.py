import re

from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_bool, parse_int, parse_children_tag_contents
from ..util import retrieve_contents

NO_POINTS = 0
FULL_POINTS = 100

question_children_names = [
    'correct', 'incorrect', 'correct-comments', 'neutral-comments', 'incorrect-comments'
]


common_fields = [
    Attribute('correct-comments', new_name='correct_comments'),
    Attribute('neutral-comments', new_name='neutral_comments'),
    Attribute('incorrect-comments', new_name='incorrect_comments'),
    Attribute('text-after-answers', new_name='text_after_answers'),
    Attribute('type', ignore=True)
]

mostly_common_fields = [
    Attribute('points', 1, parse_int, 'points_possible'),
    *common_fields
]


def parse_text_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'text_only_question',
    }
    return [question]


def parse_true_false_question(tag: Tag):
    """
    <question type='true-false' answer='true' points_possible='2'>
    The earth orbits the sun
    </question>

    <question type='true-false' answer='false'>
    The earth is **flat**

    <correct-comments>
    A nationwide survey in 2022 by researchers at the University of New Hampshire found that
    10% of U.S. adults believed the earth was flat.
    </correct-comments>

    <incorrect-comments>
    Regular folks who like math and stars rely on the curvature on the earth to track the motion
    of heavenly bodies.
    </incorrect-comments>
    </question>
    """
    fields = [
        Attribute('answer', required=True, parser=parse_bool, default=False)
    ]
    question = parse_settings(tag, mostly_common_fields + fields)

    question.update({
        "question_text": retrieve_contents(tag, question_children_names),
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

    return [question]


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
    answers = parse_children_tag_contents(tag, re.compile(r'correct|incorrect'))
    question = {
        "question_text": retrieve_contents(tag, question_children_names),
        "question_type": question_type,
        "answers": [
            {
                "answer_html": answer,
                "answer_weight": FULL_POINTS if answer in corrects else NO_POINTS
            } for answer in answers
        ]
    }
    question.update(parse_settings(tag, mostly_common_fields))
    return [question]


def parse_matching_question(tag: Tag):
    """
    <question type='matching'>
    Match the following:
    <pair left='1' right='A' />
    <pair left='2' right='B' />
    <pair left='3' right='C' /
    <distractors>
    D
    E
    </distractors>
    <correct-comments>Good job!</correct-comments>
    </question>
    """
    left_field = Attribute('left', required=True)
    right_field = Attribute('right', required=True)
    pairs = [
        parse_settings(answer, [left_field, right_field]) for answer in tag.find_all('pair')
    ]
    distractors = '\n'.join(parse_children_tag_contents(tag, 'distractors'))

    question = parse_settings(tag, mostly_common_fields)

    question.update({
        "question_text": retrieve_contents(tag, question_children_names),
        "question_type": 'matching_question',
        "points_possible": parse_int(tag.get('points') or len(pairs)),
        "answers": [
            {
                "answer_match_left": answer['left'],
                "answer_match_right": answer['right'],
                "answer_weight": FULL_POINTS
            } for answer in pairs
        ],
        "matching_answer_incorrect_matches": '\n'.join(distractors)
    })

    return [question]


def parse_multiple_true_false_question(tag: Tag):
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
    resulting_questions = []

    header = retrieve_contents(tag, question_children_names)
    resulting_questions.append({
        "question_text": header,
        "question_type": 'text_only_question',
    })

    answers = tag.find_all(re.compile(r'correct|incorrect'))

    question_attributes = [
        Attribute('points', default=len(answers), parser=parse_int, new_name='points_possible'),
    ]
    settings = parse_settings(tag, question_attributes + common_fields)
    total_points = settings['points_possible']

    # Distribute points evenly among the questions
    points_per_question = round(total_points // len(answers), 2)
    error = total_points - points_per_question * len(answers)
    num_to_change = round(error * 100)
    amount = 0.01 if error > 0 else -0.01

    for index, child in enumerate(answers):
        resulting_questions.append({
            "question_text": retrieve_contents(child),
            "question_type": 'true_false_question',
            "points_possible": points_per_question + amount if index < num_to_change else points_per_question,
            "answers": [
                {
                    "answer_text": "True",
                    "answer_weight": FULL_POINTS if child.name == 'correct' else NO_POINTS
                },
                {
                    "answer_text": "False",
                    "answer_weight": FULL_POINTS if child.name == 'incorrect' else NO_POINTS
                }
            ]
        })

    return resulting_questions


def parse_fill_in_the_blank_question(tag: Tag):
    """
    <question type='fill-in-the-blank'>
    The capital of France is [blank].
    <correct text='Paris' />
    </question>
    """
    question_text = retrieve_contents(tag, question_children_names)
    blanks = re.findall(r'\[([^]]+)]', question_text)
    if not blanks:
        raise ValueError("Fill in the blank questions must contain at least one blank!")

    answer_attributes = [
        Attribute('text', required=True, new_name='answer_text'),
        Attribute('blank_id', blanks[0]),
        Attribute('answer_weight', FULL_POINTS),
    ]

    question = {
        "question_text": retrieve_contents(tag, question_children_names),
        "question_type": 'fill_in_multiple_blanks_question',
        "answers": [
            parse_settings(answer, answer_attributes) for answer in tag.find_all('correct')
        ]
    }

    question.update(parse_settings(tag, mostly_common_fields))
    return [question]


def parse_fill_in_multiple_blanks_question(tag: Tag):
    """
    <question type='fill-in-multiple-blanks'>
    The U.S. flag has [stripes] stripes and [stars] stars.
    <correct text='13' blank='stripes' />
    <correct text='50' blank='stars' />
    </question>
    """
    answer_attributes = [
        Attribute('text', required=True, new_name='answer_text'),
        Attribute('blank', required=True, new_name='blank_id'),
        Attribute('answer_weight', FULL_POINTS)
    ]

    question = {
        "question_text": retrieve_contents(tag, question_children_names),
        "question_type": 'fill_in_multiple_blanks_question',
        "answers": [
            parse_settings(answer, answer_attributes) for answer in tag.find_all('correct')
        ]
    }
    question.update(parse_settings(tag, mostly_common_fields))
    return [question]


def parse_essay_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'essay_question',
    }
    return [question]


def parse_file_upload_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'file_upload_question',
    }
    return [question]


def parse_exact_answer_question(tag: Tag):
    """
    <question type='numerical'>
    Give one possible value for x. The margin of error is +- 0.0001.
    (x - pi)^2 = (x - pi)

    <correct type='exact' exact='3.14159' margin='0.0001' />

    <correct type='exact' exact='4.14159' margin='0.0001' />
    </question>
    """

    question_text = retrieve_contents(tag, ['exact', 'margin'])
    answer_attributes = [
        Attribute('exact', required=True),
        Attribute('margin', required=True)
    ]

    return question_text, answer_attributes


def parse_range_answer_question(tag: Tag):
    """
    <question type='numerical'>
    Give one possible value for x.
    1 <= x^2 <= 100

    <correct type='range' start='1' end='10' />

    <correct type='range' start='-10' end='-1' />
    </question>
    """
    question_text = retrieve_contents(tag, ['start', 'end'])

    answer_attributes = [
        Attribute('start', required=True),
        Attribute('end', required=True)
    ]

    return question_text, answer_attributes


def parse_precision_answer_question(tag: Tag):
    """
    The precision number is how many digits are expected in the answer.
    Precision answers can be negative numbers and may include trailing zeroes.
    However, student responses will be marked as correct if they omit the trailing zeroes, as long as all preceding digits are correct.

    <question type='numerical'>
    What is the value of pi?
    <correct type='precision' approximate='3.14159' precision='5' />
    </question>
    """

    question_text = retrieve_contents(tag, ['approximate', 'precision'])
    answer_attributes = [
        Attribute('approximate', required=True),
        Attribute('precision', required=True)
    ]

    return question_text, answer_attributes


# In development, issues with rounding decimals
def parse_numerical_question(tag: Tag):
    raise NotImplementedError()

# def parse_numerical_question(tag: Tag):
#     numerical_answer_types = {
#         'exact': parse_exact_answer_question,
#         'range': parse_range_answer_question,
#         'precision': parse_precision_answer_question
#     }
#
#     numerical_answer_type = tag.get('numerical_answer_type')
#     if numerical_answer_type not in numerical_answer_types:
#         raise ValueError(f"Invalid numerical answer type: {numerical_answer_type}")
#     question_text, answer_attributes = numerical_answer_types[numerical_answer_type](tag)
#
#     question = {
#         "question_text": question_text,
#         "question_type": 'numerical_question',
#         "answers": [
#             parse_settings(answer, answer_attributes) for answer in tag.find_all('correct')
#         ]
#     }
#
#     fields = [
#         Attribute('numerical_answer_type', required=True)
#     ]
#     question.update(parse_settings(tag, fields + common_fields))
#     return question

