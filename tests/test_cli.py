import subprocess
import sys
from pathlib import Path


def test_skilldir_prints_packaged_skills_directory():
    result = subprocess.run(
        [sys.executable, '-m', 'mdxcanvas.cli', 'skilldir'],
        check=True,
        capture_output=True,
        text=True,
    )

    skill_directory = Path(result.stdout.strip())
    assert skill_directory == Path(__file__).parents[1] / 'mdxcanvas' / 'skills'
    assert skill_directory.is_dir()
