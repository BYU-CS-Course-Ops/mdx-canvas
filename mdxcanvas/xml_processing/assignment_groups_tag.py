# TODO
# <assignment_groups>
# | Group | Weight |
# |-------|--------|
# | Homework | 10%  |
# | Projects | 40%  |
# | Exams    | 10%  |
# </assignment_groups>
# Parse that table into a dictionary
# str: int

# To deploy:
# Using the course.update() method,
# set the 'apply_assignment_group_weights' field to True
#
# # Get all assignment groups for the course
# assignment_groups = course.get_assignment_groups()
#
# Create the missing groups
#
# Map all names to IDs
#
# # Define the weights you want to set
# # Note: This should be a dict mapping group ids to their corresponding weights
# weights = {
#     'Homework': 30,
#     'Projects': 50,
#     'Exams': 20,
# }
#
# # Update the weights for each assignment group
# for group in assignment_groups:
#     group_name = group.name  # is this field available?
#     if group_name in weights:
#         new_weight = weights[group_name]
#         updated_group = group.edit(assignment_group={'group_weight': new_weight})
