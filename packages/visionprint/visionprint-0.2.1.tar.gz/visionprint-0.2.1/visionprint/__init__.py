from .main import success, info, dim, warn, error, rule, box
from .ansi import Colors

black   = Colors.BLACK
red     = Colors.RED
green   = Colors.GREEN
yellow  = Colors.YELLOW
blue    = Colors.BLUE
magenta = Colors.MAGENTA
cyan    = Colors.CYAN
white   = Colors.WHITE
grey    = Colors.GREY

__all__ = [
    "success", "info", "dim", "warn", "error", "rule", "box",
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "grey"
]