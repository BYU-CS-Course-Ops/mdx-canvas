# Example: MarkdownData Args Table for Assignments

This file is an example args table for use with `assignments.jinja`. Each row generates one Canvas assignment.

Pass to MDXCanvas with:

```bash
mdxcanvas --course-info course_info.json --args assignments_table.md assignments.jinja
```

---

| Title      | Due_At                 | Points_Possible | Assignment_Group |
|------------|------------------------|-----------------|------------------|
| Homework 1 | Jan 15, 2025, 11:59 PM | 100             | Homework         |
| Homework 2 | Jan 22, 2025, 11:59 PM | 100             | Homework         |
| Homework 3 | Jan 29, 2025, 11:59 PM | 50              | Homework         |
| Homework 4 | Feb 5, 2025, 11:59 PM  | 100             | Homework         |
| Homework 5 | Feb 12, 2025, 11:59 PM | 100             | Homework         |
