from .attributes import Attribute, parse_int, parse_bool, parse_date, parse_settings
from ..util import retrieve_contents
from .quiz_questions import parse_text_question, parse_true_false_question, parse_multiple_choice_question, \
    parse_multiple_answers_question, parse_matching_question, parse_multiple_true_false_question, \
    parse_fill_in_the_blank_question, parse_essay_question, parse_file_upload_question, parse_numerical_question, \
    parse_fill_in_multiple_blanks_question
from ..resources import ResourceManager, CanvasResource
from bs4 import Tag


class QuizTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources
        self.question_types = {
            'text': parse_text_question,
            'true-false': parse_true_false_question,
            'multiple-choice': parse_multiple_choice_question,
            'multiple-answers': parse_multiple_answers_question,
            'matching': parse_matching_question,
            'multiple-tf': parse_multiple_true_false_question,
            'fill-in-the-blank': parse_fill_in_the_blank_question,
            'fill-in-multiple-blanks': parse_fill_in_multiple_blanks_question,
            'essay': parse_essay_question,
            'file-upload': parse_file_upload_question,
            'numerical': parse_numerical_question
        }

    def __call__(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
            "questions": []
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
            name=quiz['title'],
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
            Attribute('published', parser=parse_bool),
            Attribute('one_time_results', False, parse_bool),
            Attribute('points_possible')
        ]

        return parse_settings(settings_tag, fields)

    def _parse_questions(self, questions_tag: Tag):
        questions = []
        for question in questions_tag.findAll('question', recursive=False):
            if not (question_type := question.get("type")):
                raise ValueError("Question type not specified.")
            if question_type not in self.question_types:
                raise ValueError(f"Question type {question_type} not supported. Supported types: {', '.join(self.question_types.keys())}")

            parse_tag = self.question_types[question_type]
            result = parse_tag(question)
            questions.extend(result)
        return questions
