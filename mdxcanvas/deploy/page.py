from canvasapi.course import Course

from ..resources import PageInfo


def deploy_page(course: Course, page_info: dict) -> tuple[PageInfo, None]:
    page_id = page_info["canvas_id"]

    if page_id:
        canvas_page = course.get_page(page_id)
        canvas_page.edit(wiki_page=page_info)
    else:
        canvas_page = course.create_page(wiki_page=page_info)

    page_object_info: PageInfo = {
        'id': canvas_page.page_id,
        'title': canvas_page.title,
        'page_url': canvas_page.url,
        'uri': f'/courses/{course.id}/pages/{canvas_page.url}',

        # Following fields have been observed to be missing in some cases
        'url': canvas_page.html_url if hasattr(canvas_page, 'html_url') else None
    }

    return page_object_info, None


def deploy_shell_page(course: Course, page_info: dict) -> tuple[PageInfo, None]:
    shell_page_info = page_info.copy()
    shell_page_info[
        'body'] = "<p>This is a shell page created to break a dependency cycle. The full content will be deployed later.</p>"

    return deploy_page(course, shell_page_info)
