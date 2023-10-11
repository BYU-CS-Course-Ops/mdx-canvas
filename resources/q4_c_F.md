```python
def draw_bar(bit):
    bit.left()
    while bit.front_clear():
        go(bit, None)
        bit.left()
        bit.left()
        go(bit, 'red')
        bit.left()
```