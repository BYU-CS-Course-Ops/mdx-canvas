from typing import Any

from bs4 import Tag

from .attributes import Attribute, parse_bool, parse_dict, parse_list, parse_settings, parse_int
from ..resources import ResourceManager, get_key, CanvasResource
from ..error_helpers import format_tag, get_file_path
from ..processing_context import get_current_file


def _parse_module_list(text: str) -> list[str]:
    modules = parse_list(text)
    return [get_key('module', module, 'id') for module in modules]


class ModuleTagProcessor:
    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager
        self._previous_module = None  # The id of the previous module
        self._previous_module_item = None  # The id of the previous module item
        self._previous_module_position = 1

    _module_item_type_casing = {
        "file": "File",
        "page": "Page",
        "discussion": "Discussion",
        "assignment": "Assignment",
        "quiz": "Quiz",
        "subheader": "SubHeader",
        "externalurl": "ExternalUrl",
        "externaltool": "ExternalTool"
    }

    def __call__(self, module_tag: Tag):
        fields = [
            Attribute('id', ignore=True),
            Attribute('title', required=True, new_name='name'),
            Attribute('position'),
            Attribute('published', parser=parse_bool),
            Attribute('previous-module'),
            Attribute('prerequisite_module_ids', parser=_parse_module_list)
        ]

        module_data = parse_settings(module_tag, fields)

        module_data['_comments'] = {
            'previous_module': ''
        }

        if self._previous_module is not None:
            # adding a reference to the previous module ensures this module
            #  is created after the previous one, thus preserving their
            #  relative ordering
            module_data['_comments']['previous_module'] = get_key('module', self._previous_module, 'id')

        if prev_mod := module_data.get('previous-module'):
            module_data['_comments']['previous_module'] = get_key('module', prev_mod, 'id')

        module_id = module_tag.get('id', module_data['name'])
        self._previous_module = module_id

        self._resources.add_resource(CanvasResource(
            type='module',
            id=module_id,
            data=module_data,
            content_path=str(get_current_file().resolve())
        ))

        self._previous_module_item = None
        self._previous_module_position = 1
        for item_tag in module_tag.find_all('item'):
            self._parse_module_item(module_id, item_tag)

    def _parse_module_item(self, module_rid: str, tag: Tag):
        fields = [
            Attribute('type', ignore=True),
            Attribute('position', parser=parse_int),
            Attribute('indent', parser=parse_int),
            Attribute('new_tab', True, parse_bool),
            Attribute('completion_requirement', parser=parse_dict),
            Attribute('iframe'),
            Attribute('published', parser=parse_bool),
        ]

        rtype = self._module_item_type_casing[tag['type'].lower()]
        item: dict[str, Any] = {
            'type': rtype
        }

        if rtype == 'ExternalUrl':
            fields.extend([
                Attribute('external_url', required=True),
                Attribute('title'),
                Attribute('id')
            ])
            item.update(parse_settings(tag, fields))
            if 'title' not in item:
                item['title'] = item['external_url']
            if 'id' not in item:
                item['id'] = item['title']

        elif rtype == 'SubHeader':
            fields.extend([
                Attribute('title', required=True),
                Attribute('id'),
            ])
            item.update(parse_settings(tag, fields))
            if 'id' not in item:
                item['id'] = item['title']

        elif rtype in ['Page', 'Quiz', 'Assignment', 'File']:
            fields.extend([
                Attribute('content_id', ignore=True),
                Attribute('title')
            ])

            if not (rid := tag.get('content_id')):
                raise ValueError(
                    f'Module "{rtype}" item must have "content_id" @ {format_tag(tag)}\n  in {get_file_path(tag)}')

            item.update(parse_settings(tag, fields))
            if rtype == 'Page':
                item['page_url'] = get_key('page', rid, 'page_url')
            else:
                item['content_id'] = get_key(rtype.lower(), rid, 'id')
            item['id'] = rid

        else:
            raise NotImplementedError(
                f'Unrecognized module item type "{rtype}" @ {format_tag(tag)}\n  in {get_file_path(tag)}')

        # Namespace each module item ID to the module
        # Otherwise, a resource can only be linked to a single module
        item['id'] = f'{module_rid}|{item["id"]}'
        item['module_id'] = get_key('module', module_rid, 'id')

        if prev_pos := item.get('position'):
            self._previous_module_position = prev_pos
        else:
            item['position'] = self._previous_module_position
            self._previous_module_position += 1

        item['_comments'] = {
            'previous_module_item':
                get_key('module_item', self._previous_module_item, 'id')
                if self._previous_module_item is not None
                else ''
        }
        self._previous_module_item = item['id']

        self._resources.add_resource(CanvasResource(
            type='module_item',
            id=item['id'],
            data=item,
            content_path=str(get_current_file().resolve())
        ))
