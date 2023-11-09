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