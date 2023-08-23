<quiz>
<settings title="Final" due_at="Dec 21, 2023, 11:59 PM" available_from="Dec 16, 2023, 12:00 AM" available_to="Dec 21, 2023, 11:59 PM" points_possible="40" assignment_group="Final" shuffle_answers="True" time_limit="240" allowed_attempts="1" show_correct_answers_at="Dec 21, 2023, 11:59 PM" access_code="start-final">

### Before taking the exam
Please take the course completion survey: Course Completion Survey


## Final Exam Instructions
**Please read and understand the following instructions before taking the final exam (scroll down).**

This is an exam. You are on your honor to treat this exam appropriately. You are not allowed to consult any material or people during this exam.

Please do not discuss the content of this exam with others.

You have 240 minutes (4 hours) to take this test. Most students will finish in under 90 minutes. If you need an accommodation, contact your instructor before you start the exam.

Prepare your exam space. Find a location where you can work uninterrupted and free from distraction for the full test-taking period. 

You are encouraged to have scratch paper available. 

Turn off your phone. Close all applications except your browser, and close all tabs except this one.

Only start the test once you intend to take and complete it. To start the test, you will need the passcode: **start-final**. 

Good luck!

</settings>


<question type="text">

## Instructions

The questions on this exam are divided into 8 sections.

Each section begins with a section header that presents a programming question, followed by True/False questions that present possible solutions to the problem in the section header. If the possible solution is valid, mark it as True. If it is not a valid solution, mark it as False. 

**There may be more than one valid solution in each section.**

You can think of each section as a single select-all-that-apply problem, where you get a point for each item you identify correctly as being a valid or invalid solution to the problem.

</question>

<question type = "multiple-tf">

# Questions 1-4

Given the program `counting.py`, where the number of uppercase, lowercase, and digits are printed, which implementation(s) of `count_characters` correctly produce the following execution?

**`counting.py`**

```python
def count_characters(input_string): ...
    
    
def main():
    input_string = input('Input: ')
    counts = count_characters(input_string)
    print(counts)
    

if __name__ == '__main__':
    main()

```

**Execution**
```text
python counting.py
Input: I LOVE pie (not 3.14)
(5, 6, 3)
```

<right>

```python
def count_characters(input_string):
    upper_count, lower_count, digit_count = 0, 0, 0
    for char in input_string:
        if char.isupper():
            upper_count += 1
        elif char.islower():
            lower_count += 1
        elif char.isdigit():
            digit_count += 1
    return (upper_count, lower_count, digit_count)
```
</right>

<wrong>

```python
def count_characters(input_string):
    upper_count = input_string.count('isupper')
    lower_count = input_string.count('islower')
    digit_count = input_string.count('isdigit')
    return (upper_count, lower_count, digit_count)
```
</wrong>
<wrong>

```python
def count_characters(input_string):
    upper_count, lower_count, digit_count = 0, 0, 0
    for char in input_string:
        if char.upper():
            upper_count += 1
        if char.lower():
            lower_count += 1
        if char.isdigit():
            digit_count += 1
    return (upper_count, lower_count, digit_count)
```
</wrong>
<wrong>

```python
def count_characters(input_string):
    upper_count, lower_count, digit_count = 0, 0, 0
    for word in input_string.split():
        if word.isupper():
            upper_count += 1
        elif word.islower():
            lower_count += 1
        elif word.isdigit():
            digit_count += 1
    return (upper_count, lower_count, digit_count)
```
</wrong>
</question>

<question type = "multiple-tf">
# Questions 5-8
<right>

```python
def 
```
</right>
<wrong>

trees
</wrong>
<wrong>

```python
def main():
    print('Hello, world!')
```
</wrong>
</question>

<question type = "true-false">
<right>

```python
def main():
    print('Hello, world!')
```
</right>
</question>

<question type = "matching">
<left>

1 + 2
</left>
<right>
3
</right>
<left>
2 + 2
</left>
<right>
4
</right>
<left>
3 + 2
</left>
<right>
5
</right>
</question>
</quiz>



