# md-canvas
Storing canvas content in markdown files for easy editing, sharing, and version control.

# Installation

```
pip install md-canvas
```



## Quizzes

See [sample-quiz.md](markdown-files/sample-quiz.canvas.md) for a quiz example.

The basic structure is as follows:
```xml
<quiz>
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

Similar to multiple-answers questions, multiple true/false questions can have any number of correct and incorrect answers.
The difference is how the quiz is created. Multiple true/false questions create a text question that holds the question description.
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
If there is a correct tag, the answer is `True`, or `False` if there is an incorrect tag.
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
