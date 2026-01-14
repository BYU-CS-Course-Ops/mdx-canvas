from canvasapi.course import Course

from .migration import migration
from ..resources import ModuleInfo, ModuleItemInfo


def deploy_module_item(course: Course, module_item_data: dict) -> tuple[ModuleItemInfo, None]:
    canvas_module = course.get_module(module_item_data['module_id'])
    if canvas_module is None:
        raise ValueError(f'Unable to find module {module_item_data["module_id"]}')

    if module_item_data['canvas_id'] is not None and (
            module_item := canvas_module.get_module_item(module_item_data['canvas_id'])):
        module_item.edit(module_item=module_item_data)
    else:
        module_item = canvas_module.create_module_item(module_item=module_item_data)

    return ModuleItemInfo(
        id=module_item.id,
        uri=f'/courses/{course.id}#module_{canvas_module.id}',
        url=f'{course.canvas._Canvas__requester.original_url}/courses/{course.id}#module_{canvas_module.id}'
    ), None


def deploy_module(course: Course, module_data: dict) -> tuple[ModuleInfo, None]:
    module_id = module_data["canvas_id"]

    if module_id:
        canvas_module = course.get_module(module_id)
        if 'published' not in module_data:
            module_data['published'] = canvas_module.published
        canvas_module.edit(module=module_data)
    else:
        canvas_module = course.create_module(module=module_data)

    module_object_info: ModuleInfo = {
        'id': canvas_module.id,
        'title': canvas_module.name,
        'uri': f'/courses/{course.id}#module_{canvas_module.id}',
        'url': f'{course.canvas._Canvas__requester.original_url}/courses/{course.id}'
    }

    return module_object_info, None


@migration(rtype='module_item', attr='module_id')
def get_module_id(course, resources: list[tuple[str, str, dict]]) -> dict[tuple[str, str], dict | None]:
    item_id_map = {
        module_item.id: module_item.module_id
        for module in course.get_modules()
        for module_item in module.get_module_items()
    }

    result = {(rtype, rid): {} for rtype, rid, _ in resources}

    for rtype, rid, canvas_info in resources:
        module_item_id = canvas_info.get('id')
        if module_item_id in item_id_map:
            canvas_info['module_id'] = item_id_map[module_item_id]
            result[(rtype, rid)] = canvas_info

    return result
