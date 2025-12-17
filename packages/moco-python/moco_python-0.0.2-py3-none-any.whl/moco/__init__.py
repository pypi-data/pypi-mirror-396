"""
    < moco >  Object-oriented command line interface framework for Python.
    Copyright (C) 2025  Monkeyhbd <monkeyhbd@outlook.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import sys
import shlex
import traceback
from collections import namedtuple


class MocoException(Exception):

    """ Base class of the exceptions raised in `moco`. """

    pass


class ParseError(MocoException):

    """ Parsing word list occurs error. """

    pass


class OptionMissed(MocoException):

    """ An option is required by program but not provided by user. """

    pass


class NotExecutable(MocoException):

    """ User expect to execute a command but program didn't define its execute method. """

    pass


class CommandNotFound(MocoException):

    """ Command not found. """

    pass


class _ExitInteractiveInterface(MocoException):

    pass


class _NeedCommandHelp(MocoException):

    pass


def is_short_opt(word: str):
    return not word.startswith('--') and word.startswith('-')


def is_long_opt(word: str):
    return word.startswith('--')


def is_opt(word: str):
    return word.startswith('-')

def split_short_opt(word: str):

    """ Split combined short option into separate short options.

        split_short_opt('-abc') => ['-a', '-b', '-c'] """

    assert is_short_opt(word)
    return ['-' + c for c in word.lstrip('-')]


# Option declaration data type.
_opt = namedtuple('option_declare',
                  ['name', 'alias', 'data_type', 'multi', 'description', 'is_help'])


def opt(name, alias=None, data_type='str', multi=False, description=None, is_help=False):

    """ Factory function to create `option_declare`. """

    return _opt(
        name=name,
        alias=[] if alias is None else alias,
        data_type=data_type,
        multi=multi,
        description=description,
        is_help=is_help,
    )


def opt_help():
    return opt('--help', alias=['-h'], description='Show this help message.', is_help=True)


class Parser:

    """ Parse word list by declared options. """

    def __init__(self, opts: list[_opt]=None):
        if opts is None:
            opts = []
        self.opts = opts
        # Map option alias to its option declaration.
        self.opt_map: dict[str, _opt] = {}
        for o in self.opts:
            self._add_option(o)

    def _add_option(self, o: _opt):
        self.opt_map[o.name] = o
        for name in o.alias:
            assert is_opt(name)
            self.opt_map[name] = o

    def _get_option_declare(self, word):
        is_declared = word in self.opt_map
        # Use default declaration if option not declared.
        o = self.opt_map[word] if is_declared else \
            opt(word, data_type='str', multi=False)
        return o

    def parse(self, words, help_if_empty=True):

        """ Parse word list into arguments and options. """

        if help_if_empty and len(words) == 0:
            raise _NeedCommandHelp

        args = []
        options = {}
        idx = 0

        def _parse_option(_o: _opt):

            """ Store option value, return how many words consume. """

            _idx_delta = 1
            _value = None
            if _o.data_type == 'bool':
                _value = True
                _idx_delta = 1
            elif _o.data_type == 'str':
                _value = words[idx + 1]
                _idx_delta = 2
            else:
                _value = words[idx + 1]
                _idx_delta = 2
            # Store option_value in each declared name.
            if _o.multi:
                pass
            else:
                options[_o.name] = _value
            return _idx_delta

        while idx < len(words):
            word = words[idx]
            # Parse options.
            if is_short_opt(word):
                o_names = split_short_opt(word)
                # Options in a combined short option must have bool data_type.
                # Except for the last one.
                for o_name in o_names[:-1]:
                    o_declare = self._get_option_declare(o_name)
                    if o_declare.is_help:
                        raise _NeedCommandHelp
                    if o_declare.data_type == 'bool':
                        _parse_option(o_declare)
                    else:
                        raise ParseError(f'Non bool option {o_name} occurs in combined short option {word}.')
                last_o_name = o_names[-1]
                last_o_declare = self._get_option_declare(last_o_name)
                if last_o_declare.is_help:
                    raise _NeedCommandHelp
                idx += _parse_option(last_o_declare)
            elif is_long_opt(word):
                o_declare = self._get_option_declare(word)
                if o_declare.is_help:
                    raise _NeedCommandHelp
                idx += _parse_option(o_declare)
            # Parse arguments.
            else:
                args.append(word)
                idx += 1

        return args, options


    def help(self):
        msg = ''
        no_help = True
        for o in self.opts:
            if o.description is not None:
                no_help = False
                names = o.name
                for a in o.alias:
                    names += ', ' + a
                line = '  {:<20}{}\n'.format(names, o.description)
                msg += line
        return None if no_help else msg

class Extendable:

    extend: dict[str, 'Extendable'] = {}

    description = ''

    @staticmethod
    def match(ext, words):
        # assert issubclass(ext, Extendable) or isinstance(ext, Extendable)
        for idx in range(len(words)):
            word = words[idx]
            if word in ext.extend:
                ext = ext.extend[word]
            else:
                return ext, words[idx:]
        return ext, []


    def help(self):
        msg = ''
        no_help = True
        for name in self.extend:
            e = self.extend[name]
            if e.description is not None:
                no_help = False
                line = '  {:<20}{}\n'.format(name, e.description)
                msg += line
        return None if no_help else msg


class Command(Extendable):

    parser: Parser = None

    def __init__(self, interface=None):
        self.interface = interface

    def execute(self, words):
        raise NotExecutable(f'Command {self.__class__} is not executable.')

    def execute_wrapper(self, words):
        try:
            self.execute(words)
        except _NeedCommandHelp:
            print(self.help(), end='')

    def help(self):
        msg = ''
        sort = ['description', 'commands', 'options']

        def _section(_name):
            _msg = ''
            if _name == 'description':
                if self.description is not None and self.description != '':
                    _description_help = self.description + '\n'
                    _msg += _description_help
            elif _name == 'commands':
                _extendable_help = Extendable.help(self)
                if _extendable_help is not None:
                    _msg += 'Commands:\n'
                    _msg += _extendable_help
            elif _name == 'options':
                _parser_help = None if self.parser is None else self.parser.help()
                if _parser_help is not None:
                    _msg += 'Options:\n'
                    _msg += _parser_help
            return _msg

        first_section = True
        for s in sort:
            _section_help = _section(s)
            if _section_help != '':
                if not first_section:
                    msg += '\n'
                msg += _section_help
                first_section = False

        return msg


class CommandLineInterface(Command):

    def launch(self):
        command_class, words = self.match(self.__class__, sys.argv[1:])
        assert issubclass(command_class, Command)
        command_class(self).execute_wrapper(words)

    def execute(self, words):
        print('Welcome to Moco CLI.')


class InteractiveInterface(Extendable):

    welcome = 'Moco Interactive CLI\n'

    prompt = '> '

    def __init__(self):
        self._keyboard_interrupt_cnt = 0

    def exit(self):
        raise _ExitInteractiveInterface

    def routine(self):
        try:
            # Input & lex
            try:
                line = input(self.prompt)
                self._keyboard_interrupt_cnt = 0
            except KeyboardInterrupt:
                self._keyboard_interrupt_cnt += 1
                if self._keyboard_interrupt_cnt >= 2:
                    print('\nExit')
                    raise _ExitInteractiveInterface
                else:
                    print('\nPress Ctrl+C again to exit.')
                    return
            origin_words = shlex.split(line)
            if len(origin_words) == 0:  # is empty line
                return
            # Match command.
            command_class, words = self.match(self.__class__, origin_words)
            if command_class == self.__class__:
                raise CommandNotFound(f'Command {origin_words[0]} not found.')
            command = command_class(self)
            # Execute command.
            command.execute_wrapper(words)
        except _ExitInteractiveInterface as e:
            raise e
        except KeyboardInterrupt:
            print()
        except Exception as e:
            traceback.print_exception(e)

    def mainloop(self):
        if self.welcome is not None:
            print(self.welcome)
        while True:
            try:
                self.routine()
            except _ExitInteractiveInterface:
                break

    def help(self):
        msg = ''
        sort = ['commands']

        def _section(_name):
            _msg = ''
            if _name == 'commands':
                _extendable_help = Extendable.help(self)
                if _extendable_help is not None:
                    _msg += 'Commands:\n'
                    _msg += _extendable_help
            return _msg

        first_section = True
        for s in sort:
            _section_help = _section(s)
            if _section_help != '':
                if not first_section:
                    msg += '\n'
                msg += _section_help
                first_section = False

        return msg


class Options(dict):

    pass
