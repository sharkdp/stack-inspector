# stack-inspector

A `gdb` command to inspect the size of objects on the stack.

![](https://i.imgur.com/uiDEJab.png)

## how to

Use `gdb` to navigate to a certain stack frame (run until your stack overflows or set a breakpoint somewhere). Then, simply run:
```gdb
source stack-inspector.py
stack-inspector
```
