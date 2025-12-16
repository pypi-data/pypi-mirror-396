#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
import sys
import os
import argparse
import shutil
import traceback
import pygments

from datetime import datetime
from pygments.token import Token
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit import PromptSession
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from wpy.argument import CommandArgumentParser
from wpy.argument import CommandArgumentParserFactory

from .errors import ContinueError
from .errors import CommnadNotFoundError

class CommandShell():

    parser_dict = {}
    parser = None
    _prompt_default = ''
    session = None
    HISTORY_PATH = os.path.expanduser('~/.wpy_history')

    def __init__(self):
        self.parser = self._get_parser()
        self.session = PromptSession(
            #  completer=CommandCompleter(self.parser, client),
            history = FileHistory(self.HISTORY_PATH),
            auto_suggest = AutoSuggestFromHistory(),
            complete_in_thread=True
        )

    def _get_parser(self, cmd=None):
        if cmd not in self.parser_dict:
            parser = CommandArgumentParserFactory.build_parser(cmd)
            parser.set_prompt(self.session)
            self.parser_dict[cmd] = parser
        return self.parser_dict[cmd]

    def run(self):
        self._run_shell()

    def get_left_prompt(self):
        return 'wpy> '

    def get_right_prompt(self):
        return ''

    def _run_shell(self):
        while True:
            try:
                right_prompt = ''
                text = self.session.prompt(
                    self.get_left_prompt(),
                    default = self._prompt_default,
                    rprompt = self.get_right_prompt(),
                )
                self._run_once_time(text)
            except ContinueError:
                continue
            except CommnadNotFoundError:
                print('command not found: {}'.format(text))
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self._print('ERROR: ' + str(e))
            self._end_run()

        #  print('GoodBye!')

    def _end_run(self):
        self._prompt_default = ''

    def _run_once_time(self, text):
        """运行"""
        if not text:
            return
        #  parser = self._get_parser()
        #  args = parser.parse_args(text)
        #  cmd = args.cmd
        self.parser = self._get_parser(text)

        self._run_base_cmd(text)

        if isinstance(self.parser, CommandArgumentParser):
            self.parser.run(text)
            return

        if not hasattr(self, '_' + cmd):
            raise CommnadNotFoundException()

        func = getattr(self, '_' + cmd)
        func(text)

    def _run_base_cmd(self, text):
        """运行基础命令"""
        if text.startswith('!'):
            text = text[1:]
            try:
                history_num = int(text)
                cmd = self.get_history_by_num(history_num)
                #  def _print_cmd():
                    #  print(cmd)
                #  run_in_terminal(_print_cmd)
                self._prompt_default = cmd
            except:
                raise CommnadNotFoundError()
            else:
                raise ContinueError()

    def _exit(self, text):
        raise EOFError()

    def get_history_by_num(self, num):
        """获取历史命令"""
        items = self.session.history.get_strings()
        if len(items) < num:
            return None
        return items[num - 1]

    def _print(self, text):
        tokens = list(pygments.lex(text, lexer=PythonLexer()))
        print_formatted_text(PygmentsTokens(tokens), end='')

