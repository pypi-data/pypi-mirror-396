# visionprint
A small Python utility library offering conditional & expressive styles for CLI output.

## Features
- Coherent printing style for different conditions
- Useful & customizable formatting functions
- No dependencies, made to be pragmatic

## Installation
```bash
pip install visionprint
```

## Examples
#### Basic Semantic Logging
```python
from visionprint import success, info, note, warn, error

success("Success") # Green, bold, italic
info("Info")       # Blue, italic
note("Note")       # Grey, faint
warn("Warn")       # Yellow, bold, underline
error("Error")     # Red, underline
```

#### Higher Level Formatting
```python
# the color must be imported like shown
from visionprint import rule, box, progress, red, green, blue

# for better progress visualization
from time import sleep

# Header with a proportional horizontal rule (bold)
rule("HEADER", color=red)

# Simple colored box around the message (bold) 
box("MASSIVE\nBOX", color=green, align="center")

# Styled progress bar with prefix and optional suffix.
total = 100
for i in range(total + 1):
    progress(
        prefix="Downloading", current=i, total=total,
        color=blue, width=40, suffix="Complete"
    )
    sleep(0.05) # illustrating process
```

## Reference
| Function                                        | Style                                               |
|-------------------------------------------------|-----------------------------------------------------|
| <code>success(msg: str)</code>                  | Green, bold, italic                                 |
| <code>info(msg: str)</code>                     | Blue, italic                                        |
| <code>note(msg: str)</code>                     | Grey, faint                                         |
| <code>warn(msg: str)</code>                     | Yellow, bold, underline                             |
| <code>error(msg: str)</code>                    | Red, underline                                      |
| <code>rule(msg: str, color)</code>              | Header with a proportional horizontal rule (bold)   |
| <code>box(msg: str, color, align: str)</code>   | Simple colored box around the message (bold)        |
| <code>progress(prefix: str, current: int, total: int, color=Colors.WHITE, width: int = 40, suffix: str = "")</code> | Styled progress bar with prefix and optional suffix. |

## Note
- Fully compatible with ANSI terminals
- Work in progress, more features coming soon

## License
MIT License
