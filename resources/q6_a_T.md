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