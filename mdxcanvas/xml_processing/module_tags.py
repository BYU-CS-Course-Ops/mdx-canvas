from bs4 import Tag

from .attributes import Attribute, parse_bool, parse_settings, parse_int, get_tag_path
from ..resources import ResourceManager, get_key, CanvasResource


class ModuleTagProcessor:
    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager
        self._previous_module = None  # The name of the previous module

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
            Attribute('previous-module')
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
            data=module_data
        ))

        for item_tag in module_tag.find_all('item'):
            self._parse_module_item(module_id, item_tag)

    def _parse_module_item(self, module_rid: str, tag: Tag):
        fields = [
            Attribute('type', ignore=True),
            Attribute('position', parser=parse_int),
            Attribute('indent', parser=parse_int),
            Attribute('new_tab', True, parse_bool),
            Attribute('completion_requirement'),
            Attribute('iframe'),
            Attribute('published', parser=parse_bool),
        ]

        rtype = self._module_item_type_casing[tag['type'].lower()]
        item = {
            'type': rtype
        }

        if rtype == 'ExternalUrl':
            fields.extend([
                Attribute('external_url', required=True),
                Attribute('title'),
                Attribute('id', ignore=True)
            ])
            item.update(parse_settings(tag, fields))
            if 'title' not in item:
                item['title'] = item['external_url']
            if 'id' not in item:
                item['id'] = item['title']

        elif rtype == 'SubHeader':
            fields.extend([
                Attribute('id', ignore=True),
                Attribute('title', required=True)
            ])
            item.update(parse_settings(tag, fields))
            if 'id' not in item:
                item['id'] = item['title']

        elif rtype == 'Page':
            fields.append(
                Attribute('content_id', ignore=True)
            )

            rid = tag.get('content_id')
            if rid is None:
                raise ValueError(f'Module "Page" item must have "content_id": {get_tag_path(tag)}')

            item.update(parse_settings(tag, fields))
            item['page_url'] = get_key(rtype.lower(), rid, 'uri')
            item['id'] = rid

        elif rtype in ['Quiz', 'Assignment', 'File']:
            fields.append(
                Attribute('content_id', ignore=True)
            )

            rid = tag.get('content_id')
            if rid is None:
                raise ValueError(f'Module "{rtype}" item must have "content_id": {get_tag_path(tag)}')

            item.update(parse_settings(tag, fields))
            item['content_id'] = get_key(rtype.lower(), rid, 'id')
            item['id'] = rid

        else:
            raise NotImplementedError(f'Unrecognized module item type "{rtype}": {get_tag_path(tag)}')

        item['module_id'] = get_key('module', module_rid, 'id')

        self._resources.add_resource(CanvasResource(
            type='module_item',
            id=item['id'],
            data=item
        ))
