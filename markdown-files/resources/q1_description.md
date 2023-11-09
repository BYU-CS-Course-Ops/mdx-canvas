Which image will the following code produce?



```python
from byubit import Bit

def move_paint(bit, color):
    bit.move()
    bit.paint(color)

@Bit.empty_world(5, 3)
def run(bit):
    color = 'blue'
    move_paint(bit, color)
    color = 'green'
    move_paint(bit, 'red')
    move_paint(bit, color)

if __name__ == '__main__':
    run(Bit.new_bit)
```