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