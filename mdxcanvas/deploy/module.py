from canvasapi.course import Course
from canvasapi.module import Module, ModuleItem

from .assignment import get_assignment
from .file import get_file
from .page import get_page
from .quiz import get_quiz
from .util import get_canvas_object


def _get_module(course: Course, name: str) -> Module:
    return get_canvas_object(course.get_modules, 'name', name)


def _get_module_item(module: Module, item: dict) -> ModuleItem | None:
    for module_item in module.get_module_items():
        if item['title'] == module_item.title:
            return module_item
    return None


def _delete_obsolete_module_items(module: Module, module_items: list[dict]):
    keepers = set(item['title'] for item in module_items)

    for module_item in module.get_module_items():
        if module_item.title not in keepers:
            module_item.delete()


def _add_canvas_id(course: Course, item: dict):
    # Add the content_id or page_url as described in
    # https://canvas.instructure.com/doc/api/modules.html#method.context_module_items_api.create

    if item['type'] in ['ExternalUrl', 'SubHeader']:
        # content_id not required
        return

    if item['type'] == 'Page':
        item['page_url'] = get_page(course, item['title']).url

    elif item['type'] == 'Quiz':
        item['content_id'] = get_quiz(course, item['title']).id

    elif item['type'] == 'Assignment':
        item['content_id'] = get_assignment(course, item['title']).id

    elif item['type'] == 'File':
        item['content_id'] = get_file(course, item['title']).id

    else:
        raise NotImplementedError('Module item of type ' + item['type'])


def _create_or_update_module_items(course: Course, module: Module, module_items: list[dict]):
    _delete_obsolete_module_items(module, module_items)

    # TODO - make sure the order of items matches the order in the XML

    for index, item in enumerate(module_items):

        _add_canvas_id(course, item)

        if module_item := _get_module_item(module, item):
            module_item.edit(module_item=item)
        else:
            module.create_module_item(module_item=item)


def deploy_module(course: Course, module_data: dict) -> tuple[Module, str|None]:
    name = module_data["name"]

    if canvas_module := _get_module(course, name):
        if 'published' not in module_data:
            module_data['published'] = canvas_module.published
        canvas_module.edit(module=module_data)
    else:
        canvas_module = course.create_module(module=module_data)

    _create_or_update_module_items(course, canvas_module, module_data.get('items', []))

    return canvas_module, None


lookup_module = _get_module
