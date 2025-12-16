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
from visionprint import rule, box, red, blue

# Header with a proportional horizontal rule (bold)
rule("HEADER", color=red)

# Simple colored box around the message (bold) 
box("MASSIVE\nBOX", color=blue, align="center")
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

## Note
- Fully compatible with ANSI terminals
- Work in progress, more features coming soon

## License
MIT License