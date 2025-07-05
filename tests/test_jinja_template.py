import json

from pathlib import Path
from mdxcanvas.text_processing.jinja_processing import process_jinja

def test_mdd_table_template():
    template_str = Path("test_files/mdd_table_template.input.md.jinja").read_text()

    actual_output = process_jinja(
        template_str,
        args_path=Path("test_files/mdd_table_template.args.md"),
    )

    expected_output = Path("test_files/mdd_table_template.expected.md").read_text()

    assert actual_output == expected_output, "The rendered output does not match the expected output."


def test_mdd_dictionary_template():
    template_str = Path("test_files/mdd_dictionary_template.input.md.jinja").read_text()

    actual_output = process_jinja(
        template_str,
        args_path=Path("test_files/mdd_dictionary_template.args.md"),
    )

    expected_output = Path("test_files/mdd_dictionary_template.expected.md").read_text()

    assert actual_output == expected_output, "The rendered output does not match the expected output."


def test_mdd_global_template():
    template_str = Path("test_files/mdd_global_template.input.md.jinja").read_text()
    global_args = json.loads(Path("test_files/mdd_global.args.json").read_text())

    actual_output = process_jinja(
        template_str,
        args_path=Path("test_files/mdd_global_template.args.md"),
        global_args=global_args
    )

    expected_output = Path("test_files/mdd_global_template.expected.md").read_text()

    assert actual_output == expected_output, "The rendered output does not match the expected output."

def test_mdd_args_template():
    template_str = Path("test_files/mdd_args_template.input.md.jinja").read_text()
    global_args = json.loads(Path("test_files/mdd_global.args.json").read_text())

    actual_output = process_jinja(
        template_str,
        global_args=global_args
    )

    expected_output = Path("test_files/mdd_args_template.expected.md").read_text()

    assert actual_output == expected_output, "The rendered output does not match the expected output."


if __name__ == '__main__':
    test_mdd_table_template()
    test_mdd_dictionary_template()
    test_mdd_global_template()
    test_mdd_args_template()
    print("All tests passed.")