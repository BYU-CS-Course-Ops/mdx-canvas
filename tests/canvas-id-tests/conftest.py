import pytest
from pathlib import Path

HERE = Path(__file__).parent

@pytest.fixture
def course_info_file() -> Path:
    path = HERE / "testing_course_info.json"
    assert path.exists(), f"Missing file: {path}"
    return path

# Assignment fixtures
@pytest.fixture
def main_input_file() -> Path:
    path = HERE / "test_files" / "assignments" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def updated_input_file() -> Path:
    path = HERE / "test_files" / "assignments" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

# Page fixtures
@pytest.fixture
def page_main_input_file() -> Path:
    path = HERE / "test_files" / "pages" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def page_updated_input_file() -> Path:
    path = HERE / "test_files" / "pages" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

# Quiz fixtures
@pytest.fixture
def quiz_main_input_file() -> Path:
    path = HERE / "test_files" / "quizzes" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def quiz_updated_input_file() -> Path:
    path = HERE / "test_files" / "quizzes" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

# Module fixtures
@pytest.fixture
def module_main_input_file() -> Path:
    path = HERE / "test_files" / "modules" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def module_updated_input_file() -> Path:
    path = HERE / "test_files" / "modules" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

# Announcement fixtures
@pytest.fixture
def announcement_main_input_file() -> Path:
    path = HERE / "test_files" / "announcements" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def announcement_updated_input_file() -> Path:
    path = HERE / "test_files" / "announcements" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

# Assignment Group fixtures
@pytest.fixture
def group_main_input_file() -> Path:
    path = HERE / "test_files" / "groups" / "main.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

@pytest.fixture
def group_updated_input_file() -> Path:
    path = HERE / "test_files" / "groups" / "updated.canvas.md.xml"
    assert path.exists(), f"Missing file: {path}"
    return path

