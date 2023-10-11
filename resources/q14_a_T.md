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