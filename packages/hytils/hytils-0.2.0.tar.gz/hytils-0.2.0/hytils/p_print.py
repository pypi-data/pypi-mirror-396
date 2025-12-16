from collections.abc import Callable
from enum import IntEnum


class ColorCode(IntEnum):
    red = 31
    green = 32
    orange = 33
    blue = 34
    purple = 35
    cyan = 36
    lightgrey = 37
    darkgrey = 90
    lightred = 91
    lightgreen = 92
    yellow = 93
    lightblue = 94
    pink = 95
    lightcyan = 96
    white = 97


def _color_str_template(color:ColorCode) -> str:
    return "\033[%dm{}\033[00m" % (color.value)


def function_generator(color: ColorCode) -> Callable[[object], str]:
    def _function(*values: object) -> str:
        # return _color_str_template(color).format(values[0])
        return _color_str_template(color).format(" ".join(map(str, values)))
    _function.__name__ = color.name
    _function.__doc__ = f"Return a string colored {color.name} in terminal output."
    return _function


red: Callable[[object], str] = function_generator(ColorCode.red)
green: Callable[[object], str] = function_generator(ColorCode.green)
orange: Callable[[object], str] = function_generator(ColorCode.orange)
blue: Callable[[object], str] = function_generator(ColorCode.blue)
purple: Callable[[object], str] = function_generator(ColorCode.purple)
cyan: Callable[[object], str] = function_generator(ColorCode.cyan)
lightgrey: Callable[[object], str] = function_generator(ColorCode.lightgrey)
darkgrey: Callable[[object], str] = function_generator(ColorCode.darkgrey)
lightred: Callable[[object], str] = function_generator(ColorCode.lightred)
lightgreen: Callable[[object], str] = function_generator(ColorCode.lightgreen)
yellow: Callable[[object], str] = function_generator(ColorCode.yellow)
lightblue: Callable[[object], str] = function_generator(ColorCode.lightblue)
pink: Callable[[object], str] = function_generator(ColorCode.pink)
lightcyan: Callable[[object], str] = function_generator(ColorCode.lightcyan)
white: Callable[[object], str] = function_generator(ColorCode.white)
