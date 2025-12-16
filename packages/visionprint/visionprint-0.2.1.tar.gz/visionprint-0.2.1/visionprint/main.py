from .ansi import Colors, Styles

def _print(msg: str, color: str="", bold=False, faint=False, italic=False, underline=False):
    style = ""

    if bold:      style += Styles.BOLD
    if faint:     style += Styles.FAINT
    if italic:    style += Styles.ITALIC
    if underline: style += Styles.UNDERLINE

    print(f"{style}{color}{msg}{Styles.RESET}")

# Basic Semantic Logging

def success(msg: str):
    """
    Green, bold, italic
    """
    _print(msg, color=Colors.GREEN, bold=True, italic=True)

def info(msg: str):
    """
    Blue, italic
    """
    _print(msg, color=Colors.BLUE, italic=True)

def dim(msg: str):
    """
    Grey, faint
    """
    _print(msg, Colors.GREY, faint=True)

def warn(msg: str):
    """
    Yellow, bold, underline
    """
    _print(msg, color=Colors.YELLOW, bold=True, underline=True)

def error(msg: str):
    """
    Red, underline
    """
    _print(msg, color=Colors.RED, underline=True)

# Higher Level Formatting

def rule(msg: str, color=Colors.WHITE):
    """
    Header with a proportional horizontal rule (bold)
    """
    rule_length = "-" * (len(msg) // 2)
    _print(f"{rule_length} {msg} {rule_length}", color=color, bold=True)

def box(msg: str, color=Colors.WHITE, align: str = "center"):
    """
    Simple colored box around the message (bold)
    """
    lines = msg.split("\n")
    width = max(len(line) for line in lines)
    items = "+" + "-" * (width + 2) + "+"

    _print(items, color=color, bold=True)
    for line in lines:
        if align == "center":  line = line.center(width)
        elif align == "left":  line = line.ljust(width)
        elif align == "right": line = line.rjust(width)

        _print(f"| {line} |", color=color, bold=True)
    _print(items, color=color, bold=True)