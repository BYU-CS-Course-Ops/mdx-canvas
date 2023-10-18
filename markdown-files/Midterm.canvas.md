<quiz>
<settings title="Midterm" due_at="Dec 21, 2023, 11:59 PM" available_from="Dec 16, 2023, 12:00 AM" available_to="Dec 21, 2023, 11:59 PM" points_possible="40" assignment_group="Final" shuffle_answers="True" time_limit="240" allowed_attempts="1" show_correct_answers_at="Dec 21, 2023, 11:59 PM" access_code="start-final">

## Quiz Instructions
Please read and understand the following instructions before taking the midterm.

This is an exam. You are on your honor to treat this exam appropriately. You are not allowed to consult any material or people during this exam.

You have 180 minutes (3 hours) to take this test. Most students will finish in under 90 minutes. If you need an accommodation, contact your instructor.

Prepare your exam space. Find a location where you can work uninterrupted and free from distraction for the full test-taking period. 

**You are encouraged to have scratch paper available.**

Turn off your phone. Close all applications except your browser, and close all tabs except this one.

To start the test, you will need the passcode **start-midterm**. Only start the test once you intend to take and complete it.

The correct answers will be visible starting on Saturday.

Good luck!

</settings>

<question type="text">
Some of these questions have answers that are very similar. Be sure to review all the answers for a question and not just take the first answer that looks correct.
</question>

<question type = "multiple-tf" name="Questions 1-4">

```python
from byubit import Bit

def move_paint(bit, color):
    bit.move()
    bit.paint(color)

@Bit.empty_world(5, 3)
def run(bit):
    color = 'blue'
    move_paint(bit, color)
    color = 'green'
    move_paint(bit, 'red')
    move_paint(bit, color)

if __name__ == '__main__':
    run(Bit.new_bit)
```
<correct>
![alt text](q1_bit_blue_red_green_T.PNG)
</correct>

<incorrect>
![alt text](q1_bit_blue_blue_blue_F.PNG)
</incorrect>

<incorrect>
![alt text](q1_bit_blue_green_green_F.PNG)
</incorrect>

<incorrect>
![alt text](q1_bit_blue_red_red_F.PNG)
</incorrect>
</question>

<question type = "multiple-tf" name="Questions 5-8">
Given the following starting world named `rgb`:

![q2_starting_world](./q2_start_description.svg)

Which block of code will produce the following end result:

![q2_ending_world](./q2_finish_description.svg)

<correct>

```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        elif bit.is_green():
            bit.paint('blue')
        else:
            bit.erase()

if __name__ == '__main__':
    run(Bit.new_bit)
```
</correct>

<incorrect>

```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        if bit.is_green():
            bit.paint('blue')
        else:
            bit.erase()

if __name__ == '__main__':
    run(Bit.new_bit)

```
</incorrect>

<incorrect>

```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        elif bit.is_blue():
            bit.erase()
        else:
            bit.paint('blue')

if __name__ == '__main__':
    run(Bit.new_bit)

```
</incorrect>

<incorrect>

```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        elif bit.is_green():
            bit.paint('blue')
        elif bit.is_blue():
            bit.erase()
        else:
            bit.paint('red')

if __name__ == '__main__':
    run(Bit.new_bit)

```
</incorrect>
</question>

<question type="multiple-tf"> name="Questions 9-12">
Starting with this world:

![four by four bit world; all cells white; bit in bottom left corner
](q3_start_description.svg)

Which code snippet produces this result:

![four by four bit world with blue in the cells on the edge
](q3_finish_description.svg)

<correct>

```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        while bit.front_clear():
            bit.paint('blue')
            bit.move()
        bit.left()
        
run(Bit.new_bit)
```
</correct>

<incorrect>

```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        while bit.front_clear():
            bit.paint('blue')
            bit.move()
        bit.left()

if __name__ == '__main__':
    run(Bit.new_bit)
```
</incorrect>

<incorrect>

```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        while bit.front_clear():
            bit.move()
            bit.paint('blue')
        bit.left()

if __name__ == '__main__':
    run(Bit.new_bit)
```
</incorrect>

<incorrect>

```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        bit.move()
        bit.paint('blue')
        if not bit.front_clear():
            bit.left()

if __name__ == '__main__':
    run(Bit.new_bit)
```
</incorrect>
</question>

<question type = "multiple-tf" name="Questions 13-15">
Bit starts in the following world `red_bars`:

![q4_starting_world](q4_start_description.svg)


Which of the following implementations of `draw_bar` will produce the following result?

![q4_ending_world](q4_finish_description.svg)



```python
from byubit import Bit

def go(bit, color):
    while bit.front_clear():
        bit.move()
        if color is not None:
            bit.paint(color)

def draw_bar(bit):
    pass

@Bit.worlds('red_bars')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            draw_bar(bit)

if __name__ == '__main__':
    run(Bit.new_bit)
```
<correct>

```python
def draw_bar(bit):
    bit.left()
    go(bit, 'red')
    bit.right()
    bit.right()
    go(bit, None)
    bit.left()
```
</correct>

<incorrect>

```python
def draw_bar(bit):
    go(bit, 'red')
    bit.left()
    bit.left()
    go(bit, 'red')
```
</incorrect>

<incorrect>

```python
def draw_bar(bit):
    bit.left()
    while bit.front_clear():
        go(bit, None)
        bit.left()
        bit.left()
        go(bit, 'red')
        bit.left()
```
</incorrect>

<incorrect>

```python
def draw_bar(bit):
    bit.left()
    go(bit, None)
    bit.right()
    bit.right()
    go(bit, 'red')
    bit.left()
```
</incorrect>
</question>

<question type="multiple-choice"> name="Question 16">
What does the following code print?

```python
def function1(a):
    return a + 2


def function2(a):
    return function1(a) - 5


def main():
    result = function2(3)
    print(result)

if __name__ == '__main__':
    main()
```
<correct>
`0`
</correct>

<incorrect>
`-2`
</incorrect>

<incorrect>
`3`
</incorrect>

<incorrect>
`1`
</incorrect>

</question>

<question name="Question 17">
Which block of code could produce the following dialog:

```text
Give me a fruit: pear
Those are fine.
Give me a fruit: banana
Those are fine.
Give me a fruit: apple
I like that!
Goodbye!
```

<correct>

```python
def main():
    while True:
        fruit = input('Give me a fruit: ')
        if fruit == 'apple':
            print('I like that!')
            break
        elif fruit == 'durian':
            print('No thank you!')
        else:
            print('Those are fine.')
    print('Goodbye!')

if __name__ == '__main__':
    main()
```
</correct>

<incorrect>

```python
def main():
    while True:
        fruit = input('Give me a fruit: ')
        if fruit == 'apple':
            print('I like that!')
            return
        else:
            print('Those are fine.')
    print('Goodbye!')

if __name__ == '__main__':
    main()
```
</incorrect>

<incorrect>

```python
def main():
    while True:
        fruit = input('Give me a fruit: ')
        if fruit == 'apple':
            print('I like that!')
            break
        elif fruit == 'banana':
            print('Those are ok.')
        else:
            print('Those are fine.')
    print('Goodbye!')

if __name__ == '__main__':
    main()
```
</incorrect>

<incorrect>

```python
def main():
    while True:
        fruit = input('Give me a fruit: ')
        if fruit == 'pear':
            print('Those are fine.')
            break
        elif fruit == 'banana':
            print('Those are fine.')
            break
        else:
            print('I like that!')
    print('Goodbye!')

if __name__ == '__main__':
    main()
```
</incorrect>
</question>




</quiz>