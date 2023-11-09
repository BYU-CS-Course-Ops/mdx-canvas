```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        while bit.front_clear():
            bit.paint('blue')
            bit.move()
        bit.left()

if __name__ == '__main__':
    run(Bit.new_bit)
```