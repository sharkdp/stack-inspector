import gdb
from collections import OrderedDict, namedtuple


Symbol = namedtuple('Symbol', ['size', 'typename'])


def analyze_frame(frame_nr, frame):
    info = frame.find_sal()

    if info.symtab:
        print("  #{frame_nr:<4} {function} @ {filename}:{line}\n".format(
            frame_nr=frame_nr,
            filename=info.symtab.filename,
            line=info.line,
            function=frame.function().name))

    block = frame.block()

    symbols = {}
    while block:
        if not (block.is_global or block.is_static):
            for symbol in block:
                if symbol.is_argument or symbol.is_variable:
                    if symbol.name not in symbols:
                        symbols[symbol.name] = \
                            Symbol(symbol.type.sizeof, symbol.type)

            symbols = OrderedDict(sorted(symbols.items(),
                                         key=lambda s: s[1].size,
                                         reverse=True))

            for name, (size, typename) in symbols.items():
                print("    {size:>14,}   {name} :: {typename}".format(
                        size=size,
                        name=name,
                        typename=typename))
            print()
        block = block.superblock


class StackVisualizer(gdb.Command):
    def __init__(self):
        super().__init__("stack-inspector", gdb.COMMAND_STACK)

    def invoke(self, arg, from_tty):
        print("\nstack-inspector:\n")
        backtrace = []
        frame = gdb.selected_frame()

        while frame:
            backtrace.append(frame)
            frame = frame.older()

        for frame_nr, frame in enumerate(backtrace):
            analyze_frame(frame_nr, frame)


StackVisualizer()
