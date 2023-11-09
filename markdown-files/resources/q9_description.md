Consider the following code and output.

```python
def just_keepers(things):
    keepers = []
    for thing in things:
        if keep_it(thing):
            keepers.append(thing)
    return keepers

if __name__ == '__main__':
    stuff = just_keepers([-7, 4, 12, 2, -3])
    print(stuff)
```
```text
[-7, 12]
```
Which version of `keep_it` could be used to produce that output?