# mdx-canvas

Storing canvas content in structured files
for easy editing, sharing, and version control.

# Installation

```
pip install mdxcanvas
```

## Usage

To deploy your content to Canvas, run:

```text
mdxcanvas <canvas-mdx-file>
```

You need to have `CANVAS_API_TOKEN` defined on your environment.

Your local folder must have a file named `canvas_course_info.json` with the following:

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver"
}
```

You can optionally specify the path to the course-info json with `--course-info <path to file>`.

## Quizzes

See [sample-quiz.md](markdown-files/sample-quiz.canvas.md) for a quiz example.

The basic structure is as follows:

```xml

<quiz
    title="Midterm" due_at="Dec 21, 2023, 11:59 PM" available_from="Dec 16, 2023, 12:00 AM"
          available_to="Dec 21, 2023, 11:59 PM" points_possible="40" assignment_group="Final" shuffle_answers="True"
          time_limit="240" allowed_attempts="1" show_correct_answers_at="Dec 21, 2023, 11:59 PM"
          access_code="start-final"
>
    <description>
        ## Quiz Instructions
        Please read and understand the following instructions before taking the midterm.

        This is an exam. You are on your honor to treat this exam appropriately. You are not allowed to consult any
        material or people during this exam.
    </description>
    
    <question type="free-response">
        What is the capital of France?
        <correct>Paris</correct>
    </question>
    <question type="multiple-choice">
        What is the capital of Germany?
        <incorrect>Bonn</incorrect>
        <correct>Berlin</correct>
    </question>
    <question type="matching">
        Match the following countries with their corresponding capitals.
        <pair>
            <left>France</left>
            <right>Paris</right>
        </pair>
        <pair>
            <left>Germany</left>
            <right>Berlin</right>
        </pair>
    </question>
</quiz>
```

## Settings

Each `quiz` tag has the following parameters:

### Parameters:

- title: string
    - Required: Title of the quiz
- quiz_type: string
    - default="assignment"
    - Possible values
        - practice_quiz
        - assignment
        - graded_survey
        - survey
- points_possible: integer
    - The number of points the survey is worth
    - Only applies if quiz_type is "graded_survey"
    - For assignments, the total points are determined by the sum of the questions
- assignment_group: string
    - default=None
    - Name of the group the assignment should be put in
    - E.g. "Homework", "Labs", "Quizzes"
    - Only applies if quiz_type is "assignment" or "graded_survey"
- time_limit: integer
    - default=None
    - Measured in minutes
- shuffle_answers: boolean
    - default=False
    - If true, quiz answers for multiple choice questions will be randomized for each student.
- hide_results: string
    - default=None
        - Students can see their results after each attempt
    - "always":
        - Students can never see their results
    - "until_after_last_attempt":
        - Students can only see results after their last attempt.
- show_correct_answers: boolean
    - default=True
    - Only valid if hide_results=None
    - If false, hides correct answers from students when quiz results are viewed.
- show_correct_answers_at: DateTime
    - Example date: Sep 5, 2023, 12:00 AM
      input_formats = [
      "%b %d, %Y, %I:%M %p",
      "%b %d %Y %I:%M %p",
      "%Y-%m-%dT%H:%M:%S"
      ]
        - self.date_formatter(settings_tag.get("show_correct_answers_at", None)),
- allowed_attempts: settings_tag.get("allowed_attempts", 1),
- scoring_policy: settings_tag.get("scoring_policy", "keep_highest"),
- one_question_at_a_time: settings_tag.get("one_question_at_a_time", False),
- cant_go_back: settings_tag.get("cant_go_back", False),
- access_code: settings_tag.get("access_code", None),
- due_at: self.date_formatter(settings_tag.get("due_at", None)),
- lock_at: self.date_formatter(settings_tag.get("available_to", None)),
- unlock_at: self.date_formatter(settings_tag.get("available_from", None)),
- published: settings_tag.get("published", True),
- one_time_results: settings_tag.get("one_time_results", False),

## Question Types

### Multiple choice:

```xml

<question type="multiple-choice">
    What is the capital of Germany?
    <incorrect>Bonn</incorrect>
    <correct>Berlin</correct>
    <incorrect>Munich</incorrect>
</question>
```

Multiple choice questions must have exactly one correct answer.

## Multiple answers:

```xml

<question type="multiple-answers">
    Which pieces of code print `2 + 3 = 5`?
    <incorrect>
        ```python
        print('2 ')
        print('+ ')
        print('3 ')
        print('= ')
        print('5')
        ```
    </incorrect>
    <correct>
        ```python
        print(2, '+', 3, '=', 5)
        ```
    </correct>
    <incorrect>
        ```python
        print('2+3=5')
        ```
    </incorrect>
    <correct>
        print(f'2 + 3 = {2 + 3}')
    </correct>
</question>
```

Questions with multiple answers can have any number of correct and incorrect answers.

## Multiple True/False:

```xml

<question type="multiple-tf">
    Which pieces of code print `2 + 3 = 5`?
    <incorrect>
        ```python
        print('2 ')
        print('+ ')
        print('3 ')
        print('= ')
        print('5')
        ```
    </incorrect>
    <correct>
        ```python
        print(2, '+', 3, '=', 5)
        ```
    </correct>
    <incorrect>
        ```python
        print('2+3=5')
        ```
    </incorrect>
    <correct>
        print(f'2 + 3 = {2 + 3}')
    </correct>
</question>
```

Similar to multiple-answers questions, multiple true/false questions can have any number of correct and incorrect
answers.
The difference is how the quiz is created. Multiple true/false questions create a text question that holds the question
description.
For each correct or incorrect answer, a true/false question is created.

## True / False

```xml

<question type='true-false'>
    <incorrect>
        Two wrongs make a right.
    </incorrect>
</question>
```

True / False questions need exactly one correct or incorrect answer.
If there is a correct tag, the answer is `True`.
If there is an incorrect tag, the answer is `False`
The question body is generated from the answer contents.
The choices shown will be `True` and `False`.

## Matching

```xml

<question type="matching">
    Which expressions are equal?
    <pair>
        <left>
            1 + 2
        </left>
        <right>
            3
        </right>
    </pair>
    <pair>
        <left>
            2 + 2
        </left>
        <right>
            4
        </right>
    </pair>
    <distractors>
        7
        9
    </distractors>
</question>
```

The distractors cannot contain multiple lines; they are split by new lines.
Distractors are shown listed with the right matches.
For each left match, students select a right match.

## Text

```xml

<question type="text">
    **Text questions don't have answers or points**
    *Text questions accept markdown syntax*
</question>
```




