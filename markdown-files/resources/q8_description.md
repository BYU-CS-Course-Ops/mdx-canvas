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