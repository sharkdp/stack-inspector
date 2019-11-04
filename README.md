# stack-inspector

A gdb command to inspect the stack for large objects

## how to

From within `gdb`, simply run:
```gdb
source stack-inspector.py

# navigate to a certain stack frame (e.g. run until your stack overflows)

stack-inspector
```

## example

Consider the following C++ program which crashes with a stack overflow due to the
huge local variable `bar_large_local_variable`:
``` c++
#include <array>
#include <vector>

struct Large {
  uint8_t data[16000];
};

float global = 3.4;
static const char* static_variable = "test";

void bar(int bar_param1, double bar_param2) {
  static double bar_static_variable = 3.4;

  const float bar_outer_local[4] = {1., 2., 3., 4.};

  {
    float bar_inner_local[8];
    std::array<Large, 1024> bar_large_local_variable;
  }
}

void foo(int foo_param) {
  std::array<double, 16> foo_local;
  static char foo_static = 'x';

  // Some data on the heap which will only show up
  // as the size of the control block:
  std::vector<char> main_vector(1024, 'x');

  bar(foo_param, foo_local[0]);
}

int main() {
  const char* test = "hello";

  foo(42);
}
```

Debugging this with stack-inspector:
```
(gdb) run
Starting program: /home/shark/Dropbox/Informatik/python/stack-inspector/a.out 

Program received signal SIGSEGV, Segmentation fault.
0x00005555555551f4 in bar (
    bar_param1=<error reading variable: Cannot access memory at address 0x7fffff05c34c>, 
    bar_param2=<error reading variable: Cannot access memory at address 0x7fffff05c340>) at main.cpp:11
warning: Source file is more recent than executable.
11	void bar(int bar_param1, double bar_param2) {

(gdb) source stack-inspector.py 
(gdb) stack-inspector 

stack-inspector:

  #0    bar(int, double) @ main.cpp:11

        16,384,000   bar_large_local_variable :: std::array<Large, 1024>
                32   bar_inner_local :: float [8]
                16   bar_outer_local :: const float [4]
                 8   bar_param2 :: double
                 8   bar_static_variable :: double
                 4   bar_param1 :: int

  #1    foo(int) @ main.cpp:30

               128   foo_local :: std::array<double, 16>
                24   main_vector :: std::vector<char, std::allocator<char> >
                 4   foo_param :: int
                 1   foo_static :: char

  #2    main() @ main.cpp:36

                 8   test :: const char *

```
