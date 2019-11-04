# stack-inspector

A gdb command to inspect the stack for large objects

## how to

From within `gdb`, simply run:
```gdb
source stack-inspector.py

# navigate to a certain stack frame (e.g. run until your stack overflows)

stack-inspector
```
