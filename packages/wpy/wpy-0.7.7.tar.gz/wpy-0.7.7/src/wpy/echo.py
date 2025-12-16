#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from datetime import datetime

from termcolor import colored
from termcolor import cprint

__all__ = [
    'echo', 'info', 'debug', 'error', 'warn', 'tocolor', 'red', 'blue',
    'cyan', 'green', 'grey', 'yellow', 'magenta', 'white'
]

echo = cprint

class Color(object):
    BLUE = 'blue'
    CYAN = 'cyan'
    GREEN = 'green'
    GREY = 'grey'
    RED = 'red'
    YELLOW = 'yellow'
    MAGENTA = 'magenta'
    WHITE = 'white'


def tocolor(text, fg=None, bg=None, attrs=None):
    return colored(text, fg, _fmt_bg(bg), attrs)

def echo(text, fg=None, bg=None, attrs=None, **kwargs):
    cprint(text, fg, _fmt_bg(bg), attrs, **kwargs)

def cyan(text, bg=None):
    return colored(text, Color.CYAN, _fmt_bg(bg))

def blue(text, bg=None):
    return colored(text, Color.BLUE, _fmt_bg(bg))

def green(text, bg=None):
    return colored(text, Color.GREEN, _fmt_bg(bg))

def grey(text, bg=None):
    return colored(text, Color.GREY, _fmt_bg(bg))

def red(text, bg=None):
    return colored(text, Color.RED, _fmt_bg(bg))

def yellow(text, bg=None):
    return colored(text, Color.YELLOW, _fmt_bg(bg))

def magenta(text, bg=None):
    return colored(text, Color.MAGENTA, _fmt_bg(bg))

def white(text, bg=None):
    return colored(text, Color.WHITE, _fmt_bg(bg))

def info(text):
    _logger(cyan('INFO'), text)

def debug(text):
    _logger(blue('DBUG'), text)

def error(text):
    _logger(red('EROR'), text)

def warn(text):
    _logger(yellow('WARN'), text)

def _logger(level, text):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")
    #  t = datetime.now().isoformat()
    fmt = f'[{t}] [{level}] {text}'
    print(fmt)

def _fmt_bg(color):
    if color:
        return f'on_{color}' if not color.startswith('on_') else color
    else:
        return color

if __name__ == "__main__":
    echo('hello world', Color.BLUE, Color.RED)
    info('info')
    debug('debug')
    error('error')
    warn('warn')
