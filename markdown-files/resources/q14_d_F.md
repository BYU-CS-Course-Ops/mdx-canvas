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