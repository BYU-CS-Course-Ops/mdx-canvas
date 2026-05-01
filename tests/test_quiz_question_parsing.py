from bs4 import BeautifulSoup

from mdxcanvas.xml_processing.quiz_questions import (
    parse_multiple_answers_question,
    parse_multiple_choice_question,
    parse_true_false_question,
)


def _parse_question(xml: str):
    return BeautifulSoup(xml, 'html.parser').find('question')


def test_multiple_choice_answer_comments_are_included():
    question = _parse_question("""
    <question id="q1" type="multiple-choice">
        What is the capital of France?
        <correct answer_comments="Exactly right">Paris</correct>
        <incorrect answer_comments="This is the UK capital">London</incorrect>
        <incorrect>Berlin</incorrect>
    </question>
    """)

    parsed = parse_multiple_choice_question(question)[0]

    assert parsed['answers'] == [
        {
            'answer_html': 'Paris',
            'answer_weight': 100,
            'comments_html': '<p>Exactly right</p>',
        },
        {
            'answer_html': 'London',
            'answer_weight': 0,
            'comments_html': '<p>This is the UK capital</p>',
        },
        {
            'answer_html': 'Berlin',
            'answer_weight': 0,
        },
    ]


def test_multiple_answers_answer_comments_are_included():
    question = _parse_question("""
    <question id="q1" type="multiple-answers">
        Which are programming languages?
        <correct answer_comments="Yes">Python</correct>
        <correct>JavaScript</correct>
        <incorrect answer_comments="Markup language">HTML</incorrect>
    </question>
    """)

    parsed = parse_multiple_answers_question(question)[0]

    assert parsed['answers'] == [
        {
            'answer_html': 'Python',
            'answer_weight': 100,
            'comments_html': '<p>Yes</p>',
        },
        {
            'answer_html': 'JavaScript',
            'answer_weight': 100,
        },
        {
            'answer_html': 'HTML',
            'answer_weight': 0,
            'comments_html': '<p>Markup language</p>',
        },
    ]


def test_true_false_answer_comments_are_included():
    question = _parse_question("""
    <question id="q1"
              type="true-false"
              answer="true"
              true_answer_comments="Correct"
              false_answer_comments="False is not correct here">
        The earth orbits the sun.
    </question>
    """)

    parsed = parse_true_false_question(question)[0]

    assert parsed['answers'] == [
        {
            'answer_text': 'True',
            'answer_weight': 100,
            'comments_html': '<p>Correct</p>',
        },
        {
            'answer_text': 'False',
            'answer_weight': 0,
            'comments_html': '<p>False is not correct here</p>',
        },
    ]


def test_existing_multiple_choice_without_answer_comments_still_parses():
    question = _parse_question("""
    <question id="q1" type="multiple-choice">
        2 + 2 =
        <correct>4</correct>
        <incorrect>3</incorrect>
    </question>
    """)

    parsed = parse_multiple_choice_question(question)[0]

    assert parsed['answers'] == [
        {
            'answer_html': '4',
            'answer_weight': 100,
        },
        {
            'answer_html': '3',
            'answer_weight': 0,
        },
    ]
