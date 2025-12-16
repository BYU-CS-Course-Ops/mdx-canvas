from canvasapi.course import Course
from canvasapi.module import Module, ModuleItem

from ..resources import ModuleInfo


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

    # Note: The 'id' and 'page_url' fields should have been filled in by update_links()
    # in canvas_deploy.py, which replaces @@resource||id||field@@ placeholders with actual Canvas IDs/URLs

    if item['type'] in ['ExternalUrl', 'SubHeader']:
        return

    item_type = item['type']

    if item_type == 'Page':
        if 'page_url' not in item:
            raise ValueError(f"Module item '{item['title']}' of type 'Page' missing page_url")

    elif item_type in ['Quiz', 'Assignment', 'File']:
        if 'id' in item and isinstance(item['id'], (int, str)):
            item['content_id'] = item['id']
        else:
            raise ValueError(
                f"Module item '{item['title']}' of type '{item_type}' missing valid Canvas ID. "
                f"This resource may not have been deployed yet."
            )

    else:
        raise NotImplementedError('Module item of type ' + item_type)


def _create_or_update_module_items(course: Course, module: Module, module_items: list[dict]):
    _delete_obsolete_module_items(module, module_items)

    # TODO - make sure the order of items matches the order in the XML

    for index, item in enumerate(module_items):

        _add_canvas_id(course, item)

        if module_item := _get_module_item(module, item):
            module_item.edit(module_item=item)
        else:
            module.create_module_item(module_item=item)


def deploy_module(course: Course, module_data: dict) -> tuple[ModuleInfo, None]:
    module_id = module_data["canvas_id"]

    if module_id:
        canvas_module = course.get_module(module_id)
        if 'published' not in module_data:
            module_data['published'] = canvas_module.published
        canvas_module.edit(module=module_data)
    else:
        canvas_module = course.create_module(module=module_data)

    _create_or_update_module_items(course, canvas_module, module_data.get('items', []))

    module_object_info: ModuleInfo = {
        'id': canvas_module.id
    }

    return module_object_info, None
