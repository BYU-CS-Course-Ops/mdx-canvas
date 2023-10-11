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
