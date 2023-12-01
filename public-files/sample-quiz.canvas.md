# Sample Quiz
<quiz>
<settings title="Sample Quiz" due_at="Dec 21, 2023, 11:59 PM" available_from="Dec 16, 2023, 12:00 AM" available_to="Dec 21, 2023, 11:59 PM" points_possible="40" assignment_group="Final" shuffle_answers="True" time_limit="240" allowed_attempts="1" show_correct_answers_at="Dec 21, 2023, 11:59 PM" access_code="start-final">
</settings>

<description>
These instructions are seen before taking the quiz.
</description>


<question type="text">
**This is closer to html format**

![alt text](resources/image-test.jpg)

</question>

This is a comment

<question type = "multiple-choice">
This is the question part

<correct>
This is a correct answer
</correct>

<incorrect>

![alt text](resources/image-test.jpg)

</incorrect>
</question>

<question type = "multiple-choice">
<incorrect>

```python
import random

def give_me_100():
    return random.random() * 100
```

</incorrect>

<correct>6</correct>

<incorrect>
    This is 
    incorrect
</incorrect>
</question>

<question type='true-false'>
    <correct>
        this is the question
    </correct>
</question>

<question type = "matching">

![alt text](resources/image-test.jpg)
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
</quiz>

