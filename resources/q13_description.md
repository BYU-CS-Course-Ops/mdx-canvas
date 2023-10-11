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