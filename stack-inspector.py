import gdb
from collections import OrderedDict, namedtuple


ANSI_BOLD = "\x1b[1m"
ANSI_GREEN = "\x1b[32m"
ANSI_MAGENTA = "\x1b[35m"
ANSI_CYAN = "\x1b[36m"
ANSI_RESET = "\x1b[0m"


Symbol = namedtuple('Symbol', ['size', 'typename'])


def analyze_frame(frame_nr, frame):
    info = frame.find_sal()

    if info.symtab:
        if frame.function():
            function_name = frame.function().name
        else:
            function_name = "?"
        print("  {bold}#{frame_nr:<3}{reset} "
              "{green}{function}{reset}"
              " @ "
              "{filename}:{line}\n".format(
                frame_nr=frame_nr,
                filename=info.symtab.filename,
                line=info.line,
                function=function_name,
                bold=ANSI_BOLD,
                green=ANSI_GREEN,
                reset=ANSI_RESET))
    else:
        print("  {bold}#{frame_nr:<3}{reset} Could not retrieve frame information\n".format(
            frame_nr=frame_nr,
            bold=ANSI_BOLD,
            green=ANSI_GREEN,
            reset=ANSI_RESET))
        return

    try:
        block = frame.block()
    except RuntimeError:
        print("Could not retrieve block information")
        return

    if frame.type() == gdb.INLINE_FRAME:
        print("    Frame is inlined.")
        print()
        return

    symbols = {}
    while block:
        if not (block.is_global or block.is_static):
            for symbol in block:
                # We only show symbols which are on the call stack
                # - function arguments
                # - local variables (which need frame information, no static variables)
                if symbol.is_argument or \
                        (symbol.is_variable and symbol.addr_class != gdb.SYMBOL_LOC_STATIC):
                    if symbol.name not in symbols:
                        symbols[symbol.name] = Symbol(symbol.type.sizeof, symbol.type)

        block = block.superblock

    symbols = OrderedDict(sorted(symbols.items(),
                                 key=lambda s: s[1].size,
                                 reverse=True))

    total_size = 0
    for name, (size, typename) in symbols.items():
        print("    {bold}{size:>14,}{reset}   {name} ({cyan}{typename}{reset})".format(
                size=size,
                name=name,
                typename=typename,
                cyan=ANSI_CYAN,
                magenta=ANSI_MAGENTA,
                bold=ANSI_BOLD,
                reset=ANSI_RESET
                ))
        if size:
            total_size += size

    print()

    return total_size


class StackVisualizer(gdb.Command):
    """Inspect the stack for large objects"""

    def __init__(self):
        super(StackVisualizer, self).__init__("stack-inspector", gdb.COMMAND_STACK)

    def invoke(self, arg, from_tty):
        try:
            frame = gdb.selected_frame()
        except gdb.error:
            print("[stack-inspector] could not retrieve frame information (no stack).")
            return

        backtrace = []

        while frame:
            backtrace.append(frame)
            frame = frame.older()

        print()
        total_size = 0
        for frame_nr, frame in enumerate(backtrace):
            frame_size = analyze_frame(frame_nr, frame)
            if frame_size:
                total_size += frame_size

        print("Total size: {size:,}".format(size=total_size))


StackVisualizer()
