from canvasapi.course import Course

from ..resources import PageInfo


def create_page_shell(page_data: dict) -> dict:
    """Create minimal page shell for cycle resolution"""
    return {
        'title': page_data.get('title', 'Placeholder'),
        'body': '<p>Loading...</p>',
        'published': False,
        'canvas_id': page_data.get('canvas_id')
    }


def deploy_page(course: Course, page_info: dict) -> tuple[PageInfo, None]:
    page_id = page_info["canvas_id"]

    if page_id:
        canvas_page = course.get_page(page_id)
        canvas_page.edit(wiki_page=page_info)
    else:
        canvas_page = course.create_page(wiki_page=page_info)

    # Canvas returns just the page slug (e.g., "my-page"), not the full URL
    # We need both: the slug for module items and the full URL for links
    page_slug = canvas_page.url if hasattr(canvas_page, 'url') else None
    full_url = f"/courses/{course.id}/pages/{page_slug}" if page_slug else None

    page_object_info: PageInfo = {
        'id': canvas_page.page_id,
        'url': full_url,  # Full URL for links
        'uri': full_url,  # Alias for compatibility with course_link tags
        'page_url': page_slug  # Just the slug for module items
    }

    return page_object_info, None

