```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        elif bit.is_blue():
            bit.erase()
        else:
            bit.paint('blue')

if __name__ == '__main__':
    run(Bit.new_bit)

```