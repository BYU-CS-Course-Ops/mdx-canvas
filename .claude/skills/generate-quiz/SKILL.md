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

## Instructions

When generating a quiz, please ensure the following:

1. The quiz should be wrapped in a `quiz` tag with appropriate attributes to define its settings.
2. Include a `description` tag to provide context or instructions for the quiz.
3. Populate the `questions` tag with a variety of question types as specified in the
   `/references/quiz_question_types.md`.
4. If applicable, include an `overrides` tag to customize due dates for specific course sections.
5. Ensure that the generated quiz adheres to the MDXCanvas format and standards.
6. Validate the quiz structure to ensure all tags are properly closed and nested.
7. Review the quiz for clarity, accuracy, and relevance to the specified topic or subject.
