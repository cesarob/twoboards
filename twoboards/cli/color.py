from colorama import Fore, init

init(autoreset=True)


def colorize_row(row, color):
    colorized_row = []
    for text in row:
        lines = str(text).split("\n")
        colorized_lines = map(color, lines)
        colorized_text = "\n".join(colorized_lines)
        colorized_row.append(colorized_text)
    return colorized_row


def red(v):
    return _colorize(v, Fore.RED)


def red_light(v):
    return _colorize(v, Fore.LIGHTRED_EX)


def green(v):
    return _colorize(v, Fore.GREEN)


def green_light(v):
    return _colorize(v, Fore.LIGHTGREEN_EX)


def yellow(v):
    return _colorize(v, Fore.YELLOW)


def yellow_light(v):
    return _colorize(v, Fore.LIGHTYELLOW_EX)


def blue(v):
    return _colorize(v, Fore.BLUE)


def blue_light(v):
    return _colorize(v, Fore.LIGHTBLUE_EX)


def magenta(v):
    return _colorize(v, Fore.MAGENTA)


def magenta_light(v):
    return _colorize(v, Fore.LIGHTMAGENTA_EX)


def cyan(v):
    return _colorize(v, Fore.CYAN)


def cyan_light(v):
    return _colorize(v, Fore.LIGHTCYAN_EX)


def white(v):
    return _colorize(v, Fore.WHITE)


def white_light(v):
    return _colorize(v, Fore.LIGHTWHITE_EX)


def black(v):
    return _colorize(v, Fore.BLACK)


def black_light(v):
    return _colorize(v, Fore.LIGHTBLACK_EX)


_DISABLE_COLOR = False


def disable_color():
    global _DISABLE_COLOR
    _DISABLE_COLOR = True


def _colorize(v: str, c: str) -> str:
    if _DISABLE_COLOR:
        return v
    return c + v + Fore.RESET
