from .attributes import Attribute, parse_int, parse_bool, parse_date, parse_settings
from ..util import retrieve_contents
from .quiz_questions import parse_text_question, parse_true_false_question, parse_multiple_choice_question, \
    parse_multiple_answers_question, parse_matching_question, parse_multiple_true_false_question, \
    parse_fill_in_the_blank_question, parse_essay_question, parse_file_upload_question, parse_numerical_question, \
    parse_fill_in_multiple_blanks_question, parse_fill_in_multiple_blanks_filled_answers
from ..resources import ResourceManager, CanvasResource, get_key
from bs4 import Tag
from .override_parsing import parse_overrides_container
from ..error_helpers import format_tag, get_file_path
from ..processing_context import get_current_file


class QuizTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources
        self._previous_question = None
        self.question_types = {
            'text': parse_text_question,
            'true-false': parse_true_false_question,
            'multiple-choice': parse_multiple_choice_question,
            'multiple-answers': parse_multiple_answers_question,
            'matching': parse_matching_question,
            'multiple-tf': parse_multiple_true_false_question,
            'fill-in-the-blank': parse_fill_in_the_blank_question,
            'fill-in-multiple-blanks': parse_fill_in_multiple_blanks_question,
            'fill-in-multiple-blanks-filled-answers': parse_fill_in_multiple_blanks_filled_answers,
            'essay': parse_essay_question,
            'file-upload': parse_file_upload_question,
            'numerical': parse_numerical_question
        }

    def __call__(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
        }
        quiz.update(self._parse_quiz_settings(quiz_tag))

        rid = quiz_tag.get('id', quiz['title'])

        for tag in quiz_tag.children:
            if not isinstance(tag, Tag):
                continue  # Top-level content is not supported in a quiz tag

            if tag.name == "questions":
                self._parse_questions(rid, tag)

            elif tag.name == "description":
                quiz["description"] = retrieve_contents(tag)

        info = CanvasResource(
            type='quiz',
            id=rid,
            data=quiz,
            content_path=str(get_current_file().resolve())
        )
        self._resources.add_resource(info)

        # Process <overrides> child tag if present
        for tag in quiz_tag.children:
            if isinstance(tag, Tag) and tag.name == "overrides":
                parse_overrides_container(tag, 'quiz', rid, self._resources)

    def _parse_quiz_settings(self, settings_tag):
        fields = [
            Attribute('id', ignore=True),
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
            Attribute('only_visible_to_overrides', parser=parse_bool),
            Attribute('points_possible')
        ]

        return parse_settings(settings_tag, fields)

    def _iter_questions(self, questions_tag: Tag):
        for i, tag in enumerate(questions_tag.findAll('question', recursive=False), start=1):
            question_type = tag.get("type")

            if not question_type:
                raise ValueError(f"Question type not specified @ {format_tag(tag)}\n  in {get_file_path(tag)}")

            if question_type not in self.question_types:
                raise ValueError(
                    f"Question type '{question_type}' not supported @ {format_tag(tag)}\n  Supported types: {', '.join(self.question_types.keys())}\n  in {get_file_path(tag)}")

            result = self.question_types[question_type](tag)
            name = tag.get('id', f'q{i}')
            items = result if isinstance(result, list) else [result]

            yield from ((name, j, len(items), q) for j, q in enumerate(items, start=1))

    def _parse_questions(self, quiz_rid: str, questions_tag: Tag):
        for pos, (name, idx, count, q) in enumerate(self._iter_questions(questions_tag), start=1):
            is_multi_part = count > 1

            # Multi-part questions (e.g. multiple-tf) need unique names and group tracking
            q['question_name'] = f"{name}_{idx}" if is_multi_part else name
            if is_multi_part:
                q['group_id'] = f"{quiz_rid}|{name}"

            q['id'] = f"{quiz_rid}|{q['question_name']}"
            q['quiz_id'] = get_key('quiz', quiz_rid, 'id')
            q['position'] = pos

            self._resources.add_resource(CanvasResource(
                type='quiz_question',
                id=q['id'],
                data=q,
                content_path=str(get_current_file().resolve())
            ))
