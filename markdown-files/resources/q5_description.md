What does the following code print?

```python
def function1(a):
    return a + 2


def function2(a):
    return function1(a) - 5


def main():
    result = function2(3)
    print(result)

if __name__ == '__main__':
    main()
```