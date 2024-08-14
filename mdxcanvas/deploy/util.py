def get_canvas_object(course_getter, attr_name, attr):
    objects = course_getter()
    for obj in objects:
        if obj.__getattribute__(attr_name) == attr:
            return obj
    return None


