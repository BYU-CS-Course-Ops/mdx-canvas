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

<question type = "multiple-tf" name="Questions 13-16">
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

<question type="multiple-choice"> name="Question 17">
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

<question type="multiple-tf" name="Questions 18-21">
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

<question type="multiple-tf" name="Questions 22-25">

Which of the following dialogs is **not** possible with this code?

```python
def want_pets():
    pets = []
    while True:
        pet = input('What pet do you want? ')
        if pet == '':
            break
        if pet == 'dinosaur':
            print('I want one too!')
        pets.append(pet)
    print(f'You want {len(pets)} pets.')
    if len(pets) > 3:
        print("That's too many!")

if __name__ == '__main__':
    want_pets()
```

<correct>

```text
What pet do you want? gerbil
What pet do you want? dinosaur
I want one too!
What pet do you want? dinosaur
I want one too!
What pet do you want? fish
What pet do you want? 
You want 3 pets.
```
</correct>

<incorrect>

```text
What pet do you want? dog
What pet do you want? cat
What pet do you want? bird
What pet do you want? horse
What pet do you want? 
You want 4 pets.
That's too many!
```
</incorrect>

<incorrect>

```text
What pet do you want? 
You want 0 pets.
```
</incorrect>

<incorrect>

```text
What pet do you want? dog
What pet do you want? dinosaur
I want one too!
What pet do you want? fish
What pet do you want? 
You want 3 pets.
```
</incorrect>
</question>


<question type="multiple-choice" name="Question 26">
What will the following block of code print?

```python
def loop(numbers):
    for number in numbers:
        if number % 2 == 0:
            print(number)

def dance(fruits):
    for kiwi in fruits:
        print(f'I like {kiwi}')

def main():
    numbers = [1, 4, 5, 8, 9, 12]
    dance(numbers)
    loop(numbers)

if __name__ == '__main__':
    main()
```
<correct>

```text
I like 1
I like 4
I like 5
I like 8
I like 9
I like 12
4
8
12
```
</correct>

<incorrect>

```text
I like 1
I like 5
I like 9
1
5
9
```
</incorrect>

<incorrect>

```text
I like {kiwi}
I like {kiwi}
I like {kiwi}
I like {kiwi}
I like {kiwi}
I like {kiwi}
4
8
12
```
</incorrect>

<incorrect>

```text
I like 1
I like 4
I like 5
I like 8
I like 9
I like 12
1
5
9
```
</incorrect>
</question>

<question type="multiple-tf" name="Question 27-30">

Consider the following code and output.

```python
def just_keepers(things):
    keepers = []
    for thing in things:
        if keep_it(thing):
            keepers.append(thing)
    return keepers

if __name__ == '__main__':
    stuff = just_keepers([-7, 4, 12, 2, -3])
    print(stuff)
```
```text
[-7, 12]
```
Which version of `keep_it` could be used to produce that output?

<correct>

```python
def keep_it(thing):
    return thing > 7 or thing < -5
```
</correct>

<incorrect>

```python
def keep_it(thing):
    return thing > 8 and thing < -6
```
</incorrect>

<incorrect>

```python
def keep_it(thing):
    if thing >= 12:
        return True
    elif thing < 0:
        return True
    else:
        return False
```
</incorrect>

<incorrect>

```python
def keep_it(thing):
    return thing > -3 or thing < 9
```
</incorrect>
</question>

<question type="matching" name="Question 31">
Match each `list` pattern with the scenario it serves.
<pair>
    <left>You want to add an exclamation point to each word in a list.</left>
    <right>Mapping pattern</right>
</pair>
<pair>
    <left>Eligibility is defined by highest grade, then by earliest application. You want to find the most eligible applicant.</left>
    <right>Selection pattern</right>
</pair>
<pair>
    <left>A purchase record has information about the number of items, date, and total purchase price. You want to find the total spent across a batch of purchases.</left>
    <right>Accumulator pattern</right>
</pair>
<pair>
    <left>You have a list of speech transcripts. You want only the speeches that mention prayer.</left>
    <right>Filter pattern</right>
</pair>
</question>

<question type='matching' name="Question 32">
Match each block of code with the pattern it demonstrates:

Code Block A:

```python
def find_optimal_venue(venues):
    optimal = None
    for venue in venues:
        if optimal is None or score(optimal) < score(venue):
            optimal = venue
    return optimal
```


Code Block B:

```python
def convert_to_metric(mileage_reports):
    new_reports = []
    for origin, destination, miles, time in mileage_reports:
        kilometers = convert_to_km(miles)
        new_reports.append((origin, destination, kilometers, time))
    return new_reports
```


Code Block C:

```python
def identify_priority_cases(cases):
    priorities = []
    for case in cases:
        if is_priority(case):
            priorities.append(case)
    return priorities
```


Code Block D:

```python
def count_points(games):
    total = 0
    for game in games:
        team1, team2, team1_points, team2_points, location, date = game
        total = total + team1_points + team2_points
    return total
```
<pair>
    <left>Code Block A</left>
    <right>Selection pattern</right>
</pair>
<pair>
    <left>Code Block B</left>
    <right>Mapping pattern</right>
</pair>
<pair>
    <left>Code Block C</left>
    <right>Filter pattern</right>
</pair>
<pair>
    <left>Code Block D</left>
    <right>Accumulator pattern</right>
</pair>
</question>

<question type='multiple-tf' name='Questions 33-36'>
Consider the following code:

```python
students = [
    ('Wright', 'John', 'economics', 'Oregon'),
    ('Sanchez-Moreno', 'Rosamaria', 'computer science', 'Florida')
]
```

Which code will loop through a list of student tuples and unpack them into variables?

<correct>

```python
for last, first, major, state in students:
    print(f'{first} {last} -- {major} major, from {state}')
```
</correct>

<incorrect>

```python
for every student in students:
    print(f'{student.first} {student.last} -- {student.major} major, from {student.state}')
```
</incorrect>

<incorrect>

```python
while True:
    print(f'{first} {last} -- {major} major, from {state}')
```
</incorrect>

<incorrect>

```python
for students in last, first, major, state:
    print(f'{first} {last} -- {major} major, from {state}')
```
</incorrect>
</question>

<question type='multiple-answers' name='Question 37'>
Consider the following code:

```python
def get_participant():
    first = input('First name: ')
    last = input('Last name: ')
    age = int(input('Age: '))
    if first == '' or last == '' or age < 3:
        return None

    return (first, last, age)
```


In which of the following cases would this function return `None`? (Mark all that apply)

<correct>

```text
First name: Adam
Last name:
Age: 4
```
</correct>
<incorrect>

```text
First name: Sarah
Last name: Page
Age: 10
```
</incorrect>
<incorrect>

```text
First name: 
Last name: de Souza
Age: 5
```
</incorrect>
<incorrect>

```text
First name: Preet
Last name: Bharara
Age: 2
```
</incorrect>
</question>

<question type='multiple-tf' name='Questions 38-41'>
You need to write a function that gets a person's sandwich toppings.

If they ask for onions, you need to say those are out.
Otherwise, add the topping to a list of toppings and return the list.

Which of these functions accomplishes this?

<correct>

```python
def get_toppings():
    toppings = []
    while True:
        topping = input("Topping: ")
        if topping == '':
            break
        if topping == 'onions':
            print('Sorry we are out of onions.')
        else:
            toppings.append(topping)

    return toppings
```
</correct>
<incorrect>

```python
def get_toppings():
    toppings = []
    while topping != 'onion':
        topping = input("Topping: ")

    if topping == 'onions':
        print('Sorry we are out of onions.')

    toppings.append(topping)

    return toppings
```
</incorrect>
<incorrect>

```python
def get_toppings():
    toppings = []
    while True:
        topping = input("Topping: ")
        if topping == '':
            print('Sorry we are out of onions.')
            break

        toppings.append(topping)

    return toppings
```
</incorrect>
<incorrect>

```python
def get_toppings():
    while True:
        topping = input("Topping: ")
        if topping is None:
            break
        elif topping == 'onions':
            print('Sorry we are out of onions.')
        else:
            return topping
```
</incorrect>
</question>
</quiz>






