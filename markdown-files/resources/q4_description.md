Bit starts in the following world `red_bars`:

![q4_starting_world](q4_start_description.svg)


Which of the following implementations of `draw_bar` will produce the following result?

![q4_ending_world](q4_finish_description.svg)



```python
from byubit import Bit

def go(bit, color):
    while bit.front_clear():
        bit.move()
        if color is not None:
            bit.paint(color)

def draw_bar(bit):
    pass

@Bit.worlds('red_bars')
def run(bit):
    while bit.front_clear():
        bit.move()
        if bit.is_red():
            draw_bar(bit)

if __name__ == '__main__':
    run(Bit.new_bit)
```