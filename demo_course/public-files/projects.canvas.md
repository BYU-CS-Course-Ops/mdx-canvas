<assignment>

<template-arguments>

| Title                                   | Due_At | Website_URL                      |
|-----------------------------------------|--------|----------------------------------|
| Project 1 - Bit                         | Sep 12 | homework1a-introduction-to-bit   |
| Project 2 - Decomposition with Bit      | Sep 14 | homework1b-functions             |
| Project 3 - Baseball                    | Sep 19 | homework1c-while                 |
| Project 4 - Wordle                      | Sep 21 | homework2a-if                    |
| Project 5 - Cipher                      | Sep 26 | homework2b-conditions            |

</template-arguments>
<settings title="{{ Title }}" 
    due_at="{{ Due_At }}, 2023, 8:00 AM"
    available_from="Sep 5, 2023, 12:00 AM" 
    available_to="Dec 18, 2023, 11:59 PM" 
    points_possible="150" 
    assignment_group="Projects" 
    submission_types="external_tool"
    external_tool_tag_attributes="url=https://lti.int.turnitin.com/launch/gs-proxy"
>
</settings>
<description>

Complete the project by following [these instructions](https://fall2023.byucs110.org/projects/{{ Website_URL }})

Then upload your `.py` files to Gradescope.

</description>
</assignment>
