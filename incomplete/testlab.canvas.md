<quiz>
<template-arguments>

| Id  | Due_At | Late_Due | Website_URL |
|-----|--------|----------|-------------|
| 111 | Sep 7  |          | test-lab    |

</template-arguments>

<settings title="Lab {{Id}} Quiz"
    due_at="{{ Due_At }}, 2023, 8:00 AM"
    available_from="Sep 5, 2023, 12:00 AM"
    available_to="Dec 25, 2023, 11:59 PM"
    assignment_group="Labs"
    shuffle_answers="False"
    allowed_attempts="-1">
</settings>

<description>

Complete {{Title}} [found here](https://fall2023.byucs110.org/labs/lab0-getting-started/)

Then complete this Quiz. 
<p>Paragraph 2</p>
<!-- foobar -->

</description>

<question type="true-false" points="10">
<correct>
I completed the lab activities.
</correct>
</question>

</quiz>