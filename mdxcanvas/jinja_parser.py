import csv
import json
import jinja2 as jj
from pathlib import Path


def _get_global_args(global_args_path: Path) -> dict:
    if '.json' in global_args_path.name:
        return json.loads(global_args_path.read_text())
    elif '.csv' in global_args_path.name:
        return dict(csv.DictReader(global_args_path.read_text().splitlines()))


def _process_template(template, **kwargs):
    jj_template = jj.Environment().from_string(template)
    kwargs |= dict(zip=zip, split_list=lambda x: x.split(';'))\

    return jj_template.render(**kwargs)


def process_jinja(template_file: Path, args_path: Path, global_args_path: Path = None, line_id: str = None, **kwargs) -> str:
    template = template_file.read_text()
    arg_sets = list(csv.DictReader(args_path.read_text().splitlines()))

    if global_args_path:
        global_args = _get_global_args(global_args_path)
        arg_sets = [{**args, **global_args} for args in arg_sets]

    if line_id:
        arg_sets = [arg for arg in arg_sets if arg['Id'] == line_id]

    return '\n'.join([_process_template(template, **arg, **kwargs) for arg in arg_sets])


if __name__ == '__main__':
    test_material_path = Path("../demo_course/public-files/template-material/test-template-material/")

    print(process_jinja(template_file=test_material_path / "test.canvas.xml.jinja",
                        args_path=test_material_path / "test_args.csv",
                        ))
