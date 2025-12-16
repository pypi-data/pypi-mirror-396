from .main import success, info, dim, warn, error, rule, box
from .ansi import Colors

red       = Colors.RED
light_red = Colors.LIGHT_RED
dark_red  = Colors.DARK_RED

green       = Colors.GREEN
light_green = Colors.LIGHT_GREEN
dark_green  = Colors.DARK_GREEN

blue       = Colors.BLUE
light_blue = Colors.LIGHT_BLUE
dark_blue  = Colors.DARK_BLUE

white = Colors.WHITE
grey  = Colors.GREY

reset = Colors.RESET

__all__ = [
    "success", "info", "dim", "warn", "error", "rule", "box",

    "red", "light_red", "dark_red",
    "green", "light_green", "dark_green",
    "blue", "light_blue", "dark_blue",
    "white", "grey", "reset",
]