from mdxcanvas.resources import ResourceManager
from mdxcanvas.xml_processing.xml_processing import process_canvas_xml


def test_module_position_parses_as_int():
    xml = '<module id="m1" title="Test" position="3"></module>'
    resources = process_canvas_xml(ResourceManager(), xml)
    module = resources[('module', 'm1')]
    assert module['data']['position'] == 3
    assert isinstance(module['data']['position'], int)
