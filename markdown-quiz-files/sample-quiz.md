# Sample Quiz

<settings>
title: Final
due_at: Dec 21, 2023, 11:59 PM
available_from: Dec 16, 2023, 12:00 AM
available_to: Dec 21, 2023, 11:59 PM
points_possible: 40
assignment_group: Final
shuffle_answers: True
time_limit: 240
allowed_attempts: 1
show_correct_answers_at: Dec 21, 2023, 11:59 PM
access_code: start-final
</settings>

<instructions>
These instructions are seen before taking the quiz.
</instructions>

---
This is the original format from Github, 
looks more like markdown

1. CS 110 is taught by Dr. Gordon Bean.
    - (x) True
    - ( ) False

2. CS 110 replaced CS 142.
    - (x) True
    - ( ) False 

3. What topics are taught in CS 110?
    - [x] Lists 
    - [x] Functions
    - [ ] Classes
	- [ ] ```import random```

4. Who is the president of BYU?
    - R:= C. Shane Reese

---
<question type="text">
**This is closer to html format**
</question>

<question type = "multiple-choice">
This is the question part

<right>
This is a correct answer
</right>

<wrong>
This is a multiline answer, 
which we can process fine
</wrong>
</question>

<question type="multiple-answers">
This is another question
<wrong>

```python
import random

def give_me_100():
    return random.random() * 100
```

</wrong>

<right>5</right>
<right>6</right>

<wrong>
This is 
incorrect
</wrong>


</question>


