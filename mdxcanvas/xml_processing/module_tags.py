from bs4 import Tag

from .attributes import Attribute, parse_bool, parse_settings, parse_int
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
            Attribute('title', required=True, new_name='name'),
            Attribute('position'),
            Attribute('published', parser=parse_bool)
        ]

        module_data = parse_settings(module_tag, fields)

        module_data['items'] = [
            self._parse_module_item(item_tag)
            for item_tag in module_tag.find_all('item')
        ]

        if self._previous_module is not None:
            # adding a reference to the previous module ensures this module
            #  is created after the previous one, thus preserving their
            #  relative ordering
            module_data['_comments'] = {
                'previous_module': get_key('module', self._previous_module, 'id')
            }

        self._previous_module = module_data['name']

        self._resources.add_resource(CanvasResource(
            type='module',
            name=module_data['name'],
            data=module_data
        ))

    def _parse_module_item(self, tag: Tag) -> dict:
        fields = [
            Attribute('type', ignore=True),
            Attribute('title', required=True),
            Attribute('position', parser=parse_int),
            Attribute('indent', parser=parse_int),
            Attribute('new_tab', True, parse_bool),
            Attribute('completion_requirement'),
            Attribute('iframe'),
            Attribute('published', parser=parse_bool),
        ]

        name = tag['title']
        rtype = self._module_item_type_casing[tag['type'].lower()]

        item = {
            'type': rtype
        }

        if rtype == 'Page':
            item['page_url'] = get_key(rtype.lower(), name, 'url')

        elif rtype == 'ExternalUrl':
            fields.append(Attribute(
                'external_url', required=True
            ))

        elif rtype == 'SubHeader':
            pass  # TODO - fix the fields for this (if necessary?)

        else:
            item['id'] = get_key(rtype.lower(), name, 'id')

        item.update(parse_settings(tag, fields))

        return item
