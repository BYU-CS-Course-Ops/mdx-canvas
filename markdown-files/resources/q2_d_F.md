```python
from byubit import Bit

@Bit.worlds('rgb')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            bit.paint('green')
        elif bit.is_green():
            bit.paint('blue')
        elif bit.is_blue():
            bit.erase()
        else:
            bit.paint('red')

if __name__ == '__main__':
    run(Bit.new_bit)

```