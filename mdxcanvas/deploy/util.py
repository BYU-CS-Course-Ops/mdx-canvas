def get_canvas_object(course_getter, attr_name, attr):
    objects = course_getter()
    for obj in objects:
        if obj.__getattribute__(attr_name) == attr:
            return obj
    return None


def get_canvas_uri(canvas_obj):
    html_url: str = canvas_obj.html_url[len('https://'):]
    domain_end_pos = html_url.find('/')
    return html_url[domain_end_pos:]
