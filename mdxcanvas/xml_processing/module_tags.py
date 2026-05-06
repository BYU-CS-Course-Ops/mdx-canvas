from typing import Any

from bs4.element import Tag

from .attributes import Attribute, make_id_list_parser, parse_bool, parse_dict, parse_settings, parse_int
from ..error_helpers import format_tag, get_file_path
from ..processing_context import get_current_file_str
from ..resources import ResourceManager, StrLike, get_key, CanvasResource


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
        "externaltool": "ExternalTool",
        "syllabus": "Syllabus",
    }

    def __call__(self, module_tag: Tag):
        fields = [
            Attribute('id', required=True),
            Attribute('title', required=True, new_name='name'),
            Attribute('position'),
            Attribute('published', parser=parse_bool),
            Attribute('previous-module'),
            Attribute('prerequisite_module_ids', parser=make_id_list_parser('module'))
        ]

        module_data = parse_settings(module_tag, fields)

        module_data['_comments'] = {
            'previous_module': ''
        }

        if self._previous_module:
            # adding a reference to the previous module ensures this module
            #  is created after the previous one, thus preserving their
            #  relative ordering
            module_data['_comments']['previous_module'] = get_key('module', self._previous_module, 'id')

        if prev_mod := module_data.get('previous-module'):
            module_data['_comments']['previous_module'] = get_key('module', prev_mod, 'id')

        module_id = module_data.pop('id')
        self._previous_module = module_id

        self._resources.add_resource(CanvasResource(
            type='module',
            id=module_id,
            data=module_data,
            content_path=get_current_file_str()
        ))

        self._previous_module_item = None
        self._previous_module_position = 1
        for item_tag in module_tag.find_all('item'):
            self._parse_module_item(module_id, item_tag)

    def _parse_module_item(self, module_rid: StrLike, tag: Tag):
        fields = [
            Attribute('type', ignore=True),
            Attribute('position', parser=parse_int),
            Attribute('indent', parser=parse_int),
            Attribute('new_tab', True, parse_bool),
            Attribute('completion_requirement', parser=parse_dict),
            Attribute('iframe'),
            Attribute('published', parser=parse_bool),
        ]

        rtype = self._module_item_type_casing[tag['type'].lower()]  # pyright: ignore[reportAttributeAccessIssue]
        item: dict[str, Any] = {
            'type': rtype
        }

        if rtype == 'Syllabus':
            fields.extend([
                Attribute('title'),
                Attribute('id', required=True)
            ])
            item.update(parse_settings(tag, fields))

            item['type'] = 'ExternalUrl'
            item['external_url'] = get_key('syllabus', 'syllabus', 'url')
            if 'title' not in item:
                item['title'] = 'Syllabus'

        elif rtype == 'ExternalUrl':
            fields.extend([
                Attribute('external_url', required=True),
                Attribute('title'),
                Attribute('id', required=True)
            ])
            item.update(parse_settings(tag, fields))
            if 'title' not in item:
                item['title'] = item['external_url']

        elif rtype == 'SubHeader':
            fields.extend([
                Attribute('title', required=True),
                Attribute('id', required=True),
            ])
            item.update(parse_settings(tag, fields))

        elif rtype in ['Page', 'Quiz', 'Assignment', 'File']:
            fields.extend([
                Attribute('content_id', required=True),
                Attribute('title'),
                Attribute('id')
            ])
            item.update(parse_settings(tag, fields))

            rid = tag['content_id']
            if rtype == 'Page':
                item['page_url'] = get_key('page', rid, 'page_url')
            else:
                item['content_id'] = get_key(rtype.lower(), rid, 'id')

            item['id'] = item.get('id', rid)

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
                if self._previous_module_item
                else ''
        }
        self._previous_module_item = item['id']

        self._resources.add_resource(CanvasResource(
            type='module_item',
            id=item.pop('id'),
            data=item,
            content_path=get_current_file_str()
        ))
