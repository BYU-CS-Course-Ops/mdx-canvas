from pathlib import Path

from mdxcanvas.deploy.group import deploy_group


class FakeGroup:
    def __init__(self):
        self.edits = []
        self.id = 123

    def edit(self, **kwargs):
        self.edits.append(kwargs)
        return self


class FakeCourse:
    def __init__(self):
        self.created = []
        self.updated = []
        self.group = FakeGroup()

    def get_assignment_group(self, _group_id):
        return self.group

    def create_assignment_group(self, **kwargs):
        self.created.append(kwargs)
        return self.group

    def update(self, **kwargs):
        self.updated.append(kwargs)
        return True


def test_deploy_group_enables_weighted_grades_for_weighted_groups():
    course = FakeCourse()

    deploy_group(
        course=course,
        group_data={
            'name': 'Homework',
            'group_weight': 40,
        },
        _=Path('.'),
    )

    assert course.updated == [{'course': {'apply_assignment_group_weights': True}}]


def test_deploy_group_does_not_enable_weighted_grades_for_unweighted_groups():
    course = FakeCourse()

    deploy_group(
        course=course,
        group_data={
            'name': 'Homework',
            'rules': {
                'drop_lowest': 1,
            },
        },
        _=Path('.'),
    )

    assert course.updated == []
