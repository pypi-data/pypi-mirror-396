## colors
PINK = "rgb(255,117,207)"
BLUE = "rgb(87,199,255)"
GREEN = "rgb(90,247,142)"
RED = "rgb(255,92,103)"
ORANGE = "rgb(255,201,140)"
## others
CHECK = f"[{GREEN}]✓[/]"
CROSS = f"[{RED}]✗[/]"
INDENT = " " * 3
QMARK_PREFIX = INDENT + "?"
INDENT_Q_NEWLINE = "\n" + INDENT + "  "
INFO_INDENT = INDENT + "| "
SEPARATOR = "─"*60

## store a BEAT_LENGTH for spinners to help UX
BEAT: float = 0.5
CLEAR_SLEEP: float = 0.1
DEBUG_SLEEP: float = 0.5