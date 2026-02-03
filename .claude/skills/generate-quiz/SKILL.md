---
name: generate-quiz
description: Generate a quiz when prompted with a topic, subject, or various parameters. Should be able to create all types of quiz questions supported by MDXCanvas—examples of which can be found in the `/references/"quiz_question_types.md` as well as overrides if applicable.
license: Complete terms in LICENSE.txt
---

# Quiz Tag Generation

## Overview

The `generate-quiz` skill is designed to create quizzes based on user-defined topics, subjects, or parameters.
It supports various types of quiz questions as outlined in the MDXCanvas documentation which can be found in the
`/references/quiz_question_types.md` file. As well as the ability to include overrides for specific course sections.

A quiz is defined as a collection of questions that assess knowledge on a specific topic or subject area. In
MDXCanvas quizzes are structured using a parent `quiz` tag that contains at most 3 child tags: `description`,
`questions`, and `overrides`.

## Quiz Tag

The `quiz` tag serves as the container for the entire quiz structure. It has several attributes that define its
settings, check the `/references/quiz_tag.md` for more details of this tag and its attributes.

## Quiz Question Types

The `questions` child tag contains individual question tags. Each question tag represents a different type of quiz
question. Examples of which can be found in the `/references/quiz_question_types.md` file.

## Overrides

The `overrides` child tag allows for customization of quiz due dates to specific sections of a course. This is useful
for tailoring the quiz experience based on different student groups or course structures. More information about the
`overrides` tag can be found in the `/references/override_tag.md`

## Deployment

When a user requests a quiz generation, the `generate-quiz` skill will create the quiz structure based on the
provided parameters. The generated quiz will be formatted in MDXCanvas and will include the appropriate tags and
attributes as specified.

Once generated and varified, you may be asked to deploy the quiz to Canvas via a testing course. Ask the user if
they would like to proceed with deployment after the quiz has been generated. If yes, and if it has not been given,
ask for the `course_info` CONFIG file path. Use the `deploy-to-canvas` skill to handle the deployment process.

## Templates

The `/templates/` folder contains standardized templates for consistent quiz generation:

- **`quiz_skeleton.xml`** - Base structure for all quizzes with default settings and example question types
- **`quiz_summary.md`** - Exact format for displaying quiz summaries after generation
- **`deployment_prompt.md`** - Standard prompt for asking about Canvas deployment

## Default Settings

Unless otherwise specified by the user, use these defaults for every quiz (also defined in `/templates/quiz_skeleton.xml`):

- `shuffle_answers="true"`
- `allowed_attempts="2"`
- `scoring_policy="keep_highest"`
- No time limit (omit the `time_limit` attribute)

## Question Distribution

For a quiz of N questions, aim for this mix to ensure variety:

- 30-40% multiple-choice
- 20-30% true-false
- 10-20% matching or fill-in-the-blank
- 10-20% other types (numerical, multiple-answers, essay, etc.)

Avoid using the same question type consecutively when possible.

## File Naming

Name quiz files using kebab-case: `[topic]-quiz.canvas.md.xml`

Examples:
- `lotr-quiz.canvas.md.xml`
- `python-basics-quiz.canvas.md.xml`
- `civil-war-history-quiz.canvas.md.xml`

## Output Format

After generating a quiz, ALWAYS display a summary using the exact format defined in `/templates/quiz_summary.md`.

## Instructions

When generating a quiz, please ensure the following:

1. Write the generated quiz in the following location, with priority as follows: `content` folder, `course-folder`
   folder, `root` folder.
2. The quiz should be wrapped in a `quiz` tag with appropriate attributes to define its settings (see Default
   Settings above).
3. Include a `description` tag to provide context or instructions for the quiz.
4. Populate the `questions` tag with a variety of question types as specified in the
   `/references/quiz_question_types.md` (see Question Distribution above).
5. If applicable, include an `overrides` tag to customize due dates for specific course sections.
6. Ensure that the generated quiz adheres to the MDXCanvas format and standards.
7. Validate the quiz structure to ensure all tags are properly closed and nested.
8. Review the quiz for clarity, accuracy, and relevance to the specified topic or subject.
9. Display a quiz breakdown summary using the exact format in `/templates/quiz_summary.md`.
10. End with the deployment prompt as defined in `/templates/deployment_prompt.md`.
11. If the user agrees to deploy, use the `deploy-to-canvas` skill to handle the deployment process.