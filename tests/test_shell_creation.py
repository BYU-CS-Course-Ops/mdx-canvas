import pytest
from mdxcanvas.deploy.page import create_page_shell
from mdxcanvas.deploy.assignment import create_assignment_shell
from mdxcanvas.deploy.quiz import create_quiz_shell


def test_page_shell_minimal():
    """Test page shell has minimal required fields"""
    original = {
        'title': 'My Page',
        'body': '<p>Full content with <a href="...">links</a></p>',
        'published': True,
        'editing_roles': 'teachers'
    }

    shell = create_page_shell(original)

    assert 'title' in shell
    assert shell['title'] == 'My Page'
    assert 'body' in shell
    assert len(shell['body']) < len(original['body'])  # Should be shorter
    assert shell['published'] is False  # Should be unpublished
    assert 'canvas_id' in shell
    assert shell['canvas_id'] is None  # Original didn't have canvas_id


def test_page_shell_preserves_canvas_id():
    """Test page shell preserves canvas_id for updates"""
    original = {
        'title': 'My Page',
        'body': '<p>Content</p>',
        'canvas_id': 12345
    }

    shell = create_page_shell(original)

    assert shell['canvas_id'] == 12345


def test_page_shell_with_missing_title():
    """Test page shell uses placeholder when title missing"""
    original = {
        'body': '<p>Content</p>'
    }

    shell = create_page_shell(original)

    assert shell['title'] == 'Placeholder'


def test_assignment_shell_minimal():
    """Test assignment shell has minimal required fields"""
    original = {
        'name': 'My Assignment',
        'description': '<p>Full description with instructions</p>',
        'points_possible': 100,
        'submission_types': ['online_text_entry', 'online_upload'],
        'published': True,
        'due_at': '2024-12-01T23:59:00'
    }

    shell = create_assignment_shell(original)

    assert 'name' in shell
    assert shell['name'] == 'My Assignment'
    assert 'description' in shell
    assert len(shell['description']) < len(original['description'])
    assert 'points_possible' in shell
    assert shell['points_possible'] == 100  # Preserved from original
    assert shell['submission_types'] == ['none']  # Minimal type
    assert shell['published'] is False


def test_assignment_shell_default_points():
    """Test assignment shell uses default points when not specified"""
    original = {
        'name': 'My Assignment',
        'description': '<p>Description</p>'
    }

    shell = create_assignment_shell(original)

    assert shell['points_possible'] == 0


def test_assignment_shell_preserves_canvas_id():
    """Test assignment shell preserves canvas_id"""
    original = {
        'name': 'My Assignment',
        'description': '<p>Description</p>',
        'canvas_id': 54321
    }

    shell = create_assignment_shell(original)

    assert shell['canvas_id'] == 54321


def test_quiz_shell_minimal():
    """Test quiz shell has minimal required fields"""
    original = {
        'title': 'My Quiz',
        'description': '<p>Full quiz description</p>',
        'quiz_type': 'assignment',
        'questions': [
            {'question_name': 'Q1', 'question_text': 'What is...', 'points_possible': 10},
            {'question_name': 'Q2', 'question_text': 'How to...', 'points_possible': 10}
        ],
        'published': True,
        'time_limit': 60
    }

    shell = create_quiz_shell(original)

    assert 'title' in shell
    assert shell['title'] == 'My Quiz'
    assert 'description' in shell
    assert len(shell['description']) < len(original['description'])
    # Key difference: no questions in shell
    assert 'questions' not in shell or len(shell.get('questions', [])) == 0
    assert shell['published'] is False
    assert shell['quiz_type'] == 'assignment'


def test_quiz_shell_preserves_canvas_id():
    """Test quiz shell preserves canvas_id"""
    original = {
        'title': 'My Quiz',
        'description': '<p>Description</p>',
        'canvas_id': 99999
    }

    shell = create_quiz_shell(original)

    assert shell['canvas_id'] == 99999


def test_quiz_shell_with_missing_title():
    """Test quiz shell uses placeholder when title missing"""
    original = {
        'description': '<p>Description</p>'
    }

    shell = create_quiz_shell(original)

    assert shell['title'] == 'Placeholder'


def test_shell_unpublished_state():
    """Test all shells are created in unpublished state"""
    page_shell = create_page_shell({'title': 'Test', 'published': True})
    assignment_shell = create_assignment_shell({'name': 'Test', 'published': True})
    quiz_shell = create_quiz_shell({'title': 'Test', 'published': True})

    assert page_shell['published'] is False
    assert assignment_shell['published'] is False
    assert quiz_shell['published'] is False
