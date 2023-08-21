import update_canvas as updater
from canvasapi.assignment import Assignment
from dateutil.parser import isoparse
from datetime import datetime


def has_due_date(a: Assignment) -> bool:
    return a.due_at is not None


def past_due(a: Assignment) -> bool:
    return has_due_date(a) and isoparse(a.due_at).replace(tzinfo=None) < datetime.now()


def set_default_grade(course):
    update_number = updater.prompt_for_update_type()

    # Run from most recent to the start of the semester
    due = [a for a in course.get_assignments() if past_due(a)]
    sorted_due = sorted(due, key=lambda a: a.due_at, reverse=True)

    ids_to_names = updater.get_canvas_id_to_sorted_name(course)

    # Update missing submissions to have a grade of 0
    no_update_counter = 0
    for assignment in sorted_due:
        modified = 0
        print(assignment.name)
        for submission in assignment.get_submissions():
            if submission.grade is None:
                id = ids_to_names.get(submission.user_id, submission.user_id)
                print(f"Modifying score to 0 for user: {id}")
                submission.edit(submission={"posted_grade": 0})
                modified += 1
        # Stop when no submissions are modified
        if not modified:
            no_update_counter += 1
            if no_update_counter == update_number:
                break


def main():
    canvas = updater.get_canvas_from_secrets()
    course = updater.get_course_via_prompt(canvas)
    set_default_grade(course)


if __name__ == '__main__':
    main()
