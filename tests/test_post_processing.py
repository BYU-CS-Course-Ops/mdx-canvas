from datetime import datetime
import mdxcanvas.deploy.canvas_deploy as canvas_deploy

def test_timestamp_tag(monkeypatch):
    fixed = datetime(2000, 1, 11, 1, 0, 0)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is None else fixed.astimezone(tz)

    monkeypatch.setattr(canvas_deploy, "datetime", FixedDatetime)

    data = 'This is when: <timestamp/>'
    expected = 'This is when: January 11, 2000 at 01:00 AM'
    assert canvas_deploy.post_process_resource(data) == expected

    data = 'This is when: <timestamp format="%D" />'
    expected = 'This is when: 01/11/00'
    assert canvas_deploy.post_process_resource(data) == expected

    data = "This is when: <timestamp format='%D' />"
    expected = 'This is when: 01/11/00'
    assert canvas_deploy.post_process_resource(data) == expected

    data = "<timestamp/> <timestamp format='%D' /> <timestamp/>"
    expected = 'January 11, 2000 at 01:00 AM 01/11/00 January 11, 2000 at 01:00 AM'
    assert canvas_deploy.post_process_resource(data) == expected

    data = "<timestamp format='%D'></timestamp>"
    expected = '01/11/00'
    assert canvas_deploy.post_process_resource(data) == expected
