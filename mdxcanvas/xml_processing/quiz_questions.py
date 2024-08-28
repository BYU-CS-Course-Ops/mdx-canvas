import re

from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_bool, parse_child_tag_contents, \
    parse_int, parse_children_tag_contents
from ..util import retrieve_contents

NO_POINTS = 0
FULL_POINTS = 100


common_fields = [
    Attribute('points', 1, parse_int, 'points_possible'),
    Attribute('correct-comments', new_name='correct_comments'),
    Attribute('neutral-comments', new_name='neutral_comments'),
    Attribute('incorrect-comments', new_name='incorrect_comments'),
    Attribute('text-after-answers', new_name='text_after_answers'),
    Attribute('type', recognize_and_discard=True)
]


def parse_text_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'text_only_question',
    }
    return question


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
    question = parse_settings(tag, common_fields + fields)

    question.update({
        "question_text": retrieve_contents(tag, ['correct', 'incorrect', 'correct-comments', 'incorrect-comments']),
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
    answers = parse_children_tag_contents(tag, re.compile(r'correct|incorrect'))
    question = {
        "question_text": retrieve_contents(tag, ['correct', 'incorrect', 'correct-comments', 'incorrect-comments']),
        "question_type": question_type,
        "answers": [
            {
                "answer_html": answer,
                "answer_weight": FULL_POINTS if answer in corrects else NO_POINTS
            } for answer in answers
        ]
    }
    question.update(parse_settings(tag, common_fields))
    return question


def parse_matching_question(tag: Tag):
    """
    <question type='matching'>
    Match the following:
    <pair>
        <left> 1 </left> <right> A </right>
    </pair>
    <pair>
    `<left> 2 </left> <right> B </right>
    </pair>
    <pair>
    `<left> 3 </left> <right> C </right>
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

    question = parse_settings(tag, common_fields)

    question.update({
        "question_text": retrieve_contents(tag, ['pair', 'distractor', 'correct-comments', 'incorrect-comments']),
        "question_type": 'matching_question',
        "points_possible": parse_int(tag.get('points') or len(matches)),
        "answers": [
            {
                "answer_match_left": answer_left,
                "answer_match_right": answer_right,
                "answer_weight": FULL_POINTS
            } for answer_left, answer_right in matches
        ],
        "matching_answer_incorrect_matches": '\n'.join(distractors)
    })

    return question


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

    answers = parse_children_tag_contents(tag, re.compile(r'correct|incorrect'))
    corrects = parse_children_tag_contents(tag, 'correct')

    question = parse_settings(tag, common_fields)

    question.update({
        "question_text": retrieve_contents(tag, ['correct', 'incorrect', 'correct-comments', 'incorrect-comments']),
        "question_type": 'matching_question',
        "points_possible": parse_int(tag.get('points') or len(answers)),
        "answers": [
            {
                "answer_match_left": answer,
                "answer_match_right": 'True' if answer in corrects else 'False',
                "answer_weight": FULL_POINTS
            } for answer in answers
        ]
    })
    return question


def parse_fill_in_the_blank_question(tag: Tag):
    """
    <question type='fill-in-the-blank'>
    The capital of France is [blank].
    <correct>Paris</correct>
    <incorrect>London</incorrect>
    <incorrect>Rome</incorrect>
    <incorrect>Madrid</incorrect>
    </question>
    """
    return _parse_multiple_option_question('fill_in_multiple_blanks_question', tag)


def parse_essay_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'essay_question',
    }
    return question


def parse_file_upload_question(tag: Tag):
    question_text = retrieve_contents(tag)
    question = {
        "question_text": question_text,
        "question_type": 'file_upload_question',
    }
    return question


def parse_exact_answer_question(tag: Tag):
    """
    <question type='numerical'>
    Give one possible value for x. The margin of error is +- 0.0001.
    (x - pi)^2 = (x - pi)

    <answer type='exact' exact='3.14159' margin='0.0001' />

    <answer type='exact' exact='4.14159' margin='0.0001' />
    </question>
    """

    question_text = retrieve_contents(tag, ['exact', 'margin'])
    answer_attributes = [
        Attribute('exact', required=True),
        Attribute('margin', required=True)
    ]

    question = {
        "question_text": question_text,
        "question_type": 'numerical_question',
        "answers": [
            parse_settings(answer, answer_attributes) for answer in tag.find_all('answer')
        ]
    }
    return question


def parse_range_answer_question(tag: Tag):
    """
    <question type='numerical'>
    Give one possible value for x.
    1 <= x^2 <= 100

    <answer type='range' start='1' end='10' />

    <answer type='range' start='-10' end='-1' />
    </question>
    """
    question_text = retrieve_contents(tag, ['start', 'end'])

    answer_attributes = [
        Attribute('start', required=True),
        Attribute('end', required=True)
        ]

    question = {
        "question_text": question_text,
        "question_type": 'numerical_question',
        "answers": [
            parse_settings(answer, answer_attributes) for answer in tag.find_all('answer')
        ]
    }
    return question


def parse_precision_answer_question(tag: Tag):
    """
    The precision number is how many digits are expected in the answer.
    Precision answers can be negative numbers and may include trailing zeroes.
    However, student responses will be marked as correct if they omit the trailing zeroes, as long as all preceding digits are correct.

    <question type='numerical'>
    What is the value of pi?
    <answer type='precision' approximate='3.14159' precision='5' />
    </question>
    """

    question_text = retrieve_contents(tag, ['approximate', 'precision'])
    answer_attributes = [
        Attribute('approximate', required=True),
        Attribute('precision', required=True)
    ]

    question = {
        "question_text": question_text,
        "question_type": 'numerical_question',
        "answers": [
            parse_settings(answer, answer_attributes) for answer in tag.find_all('answer')
        ]
    }
    return question


def parse_numerical_question(tag: Tag):
    numerical_answer_types = {
        'exact': parse_exact_answer_question,
        'range': parse_range_answer_question,
        'precision': parse_precision_answer_question
    }

    numerical_answer_type = tag.get('numerical_answer_type')
    if numerical_answer_type not in numerical_answer_types:
        raise ValueError(f"Invalid numerical answer type: {numerical_answer_type}")

    question = numerical_answer_types[numerical_answer_type]
    return question(tag)




#
# // Used in numerical questions.  Values can be 'exact_answer', 'range_answer',
#   // or 'precision_answer'.
#   "numerical_answer_type": "exact_answer",
#   // Used in numerical questions of type 'exact_answer'.  The value the answer
#   // should equal.
#   "exact": 42,
#   // Used in numerical questions of type 'exact_answer'. The margin of error
#   // allowed for the student's answer.
#   "margin": 4,
#   // Used in numerical questions of type 'precision_answer'.  The value the answer
#   // should equal.
#   "approximate": 1234600000.0,
#   // Used in numerical questions of type 'precision_answer'. The numerical
#   // precision that will be used when comparing the student's answer.
#   "precision": 4,
#   // Used in numerical questions of type 'range_answer'. The start of the allowed
#   // range (inclusive).
#   "start": 1,
#   // Used in numerical questions of type 'range_answer'. The end of the allowed
#   // range (inclusive).
#   "end": 10,