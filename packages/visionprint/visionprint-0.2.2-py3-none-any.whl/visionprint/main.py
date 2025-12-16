from .ansi import Colors, Styles

def _print(msg: str, color: str="", bold=False, faint=False, italic=False, underline=False, end="\n", flush=False):
    style = ""

    if bold:      style += Styles.BOLD
    if faint:     style += Styles.FAINT
    if italic:    style += Styles.ITALIC
    if underline: style += Styles.UNDERLINE

    print(f"{style}{color}{msg}{Styles.RESET}", end=end, flush=flush)

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
    Args:
        color: Choose any optional color from the Colors class
    """
    rule_length = "-" * (len(msg) // 2)
    _print(f"{rule_length} {msg} {rule_length}", color=color, bold=True)

def box(msg: str, color=Colors.WHITE, align: str = "center"):
    """
    Simple colored box around the message (bold)
    Args:
        color: Choose any optional color from the Colors class
        align: Text alignment: "left", "right" or "center"
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

def progress(prefix: str, current: int, total: int, color=Colors.WHITE, width: int = 40, suffix: str = ""):
    """
    Styled progress bar with prefix and optional suffix.
    Args:
        prefix: Description to display before the bar
        current: Current progress (int, 0 <= current <= total)
        total: Total value to reach (int, total > 0)
        color: Choose any optional color from the Colors class
        width: Width of the progress bar (int, width >= 1)
        suffix: Optional description to display after the bar
    """

    if not isinstance(current, int) or not isinstance(total, int):
        raise TypeError("current and total must be integers")
    if total <= 0:
        raise ValueError("total must be greater than 0")
    if current < 0:
        raise ValueError("current must be greater than or equal to 0")
    if current > total:
        raise ValueError("current value cannot exceed total value")
    if width <= 0:
        raise ValueError("width must be greater than 0")
    
    current  = max(0, min(current, total))
    fraction = current / total
    filled   = int(width * fraction)
    bar      = "#" * filled + "-" * (width - filled)
    percent  = f"{int(fraction * 100):3d}%"

    msg = f"{prefix}: [{bar}] {percent} {suffix}"

    _print(msg, color=color, bold=True, end="\r", flush=True)
    if current == total:
        print()