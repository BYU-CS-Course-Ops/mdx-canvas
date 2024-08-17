from bs4 import Tag

from .attributes import Attribute, parse_bool, parse_settings, parse_int
from ..resources import ResourceManager, get_key, CanvasResource


class ModuleTagProcessor:
    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager

    def __call__(self, module_tag: Tag):
        fields = [
            Attribute('title', required=True, new_name='name'),
            Attribute('position'),
            Attribute('published', default=False, parser=parse_bool)
        ]

        module_data = parse_settings(module_tag, fields)

        module_data['items'] = [
            self._parse_module_item(item_tag)
            for item_tag in module_tag.find_all('item')
        ]

        self._resources.add_resource(CanvasResource(
            type='module',
            name=module_data['name'],
            data=module_data
        ))

    casing = {
        "file": "File",
        "page": "Page",
        "discussion": "Discussion",
        "assignment": "Assignment",
        "quiz": "Quiz",
        "subheader": "SubHeader",
        "externalurl": "ExternalUrl",
        "externaltool": "ExternalTool"
    }

    def _parse_module_item(self, tag: Tag) -> dict:
        fields = [
            Attribute('title', required=True),
            Attribute('position', parser=parse_int),
            Attribute('indent', parser=parse_int),
            Attribute('new_tab', True, parse_bool),
            Attribute('completion_requirement'),
            Attribute('iframe'),
            Attribute('published', False, parse_bool),
        ]

        name = tag['title']
        rtype = self.casing[tag['type'].lower()]

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
            pass  # TODO - fix the fields for this

        else:
            item['id'] = get_key(rtype.lower(), name, 'id')

        item.update(parse_settings(tag, fields))

        return item
