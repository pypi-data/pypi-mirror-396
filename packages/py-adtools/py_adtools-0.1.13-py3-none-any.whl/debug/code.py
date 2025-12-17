
code = """
def f():
    a = f'''\
    ```python
import torch.nn as nn

class Arch(nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(x):
        return x
```
'''
    b = f'''\
    ```python
    import torch.nn as nn

    class Arch(nn.Module):
        def __init__(self):
            super().__init__()
        
        def forward(x):
            return x
    ```
    '''
    print(a)
    print("====================")
    print(b)
    print("====================")
    print(a == b)

f()
"""

from adtools import PyProgram

code = PyProgram.from_text(code)
print(code.functions[0])