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