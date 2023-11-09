```python
from byubit import Bit

@Bit.empty_world(4, 4)
def run(bit):
    while not bit.is_blue():
        bit.move()
        bit.paint('blue')
        if not bit.front_clear():
            bit.left()

if __name__ == '__main__':
    run(Bit.new_bit)
```