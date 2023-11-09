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