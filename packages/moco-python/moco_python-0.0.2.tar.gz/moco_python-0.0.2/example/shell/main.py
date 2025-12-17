from moco import InteractiveInterface, Command, Parser, opt, opt_help


class CommandHello(Command):

    description = 'Hello world.'

    def execute(self, words):
        print('Hello, this is a command!')


class CommandParse(Command):

    description = 'Parse options and arguments.'

    parser = Parser([
        opt('--host', description='Server\'s hostname.'),
        opt('--port', description='Server\'s port number.'),
        opt('--username', alias=['-u'], description='Login username.'),
        opt('--password', alias=['-P'], description='Login password.'),
        opt_help(),
    ])

    def execute(self, words):
        if '-h' in words or '--help' in words or len(words) == 0:
            print(self.help(), end='')
            return
        args, opts = self.parser.parse(words)
        print(args)
        print(opts)


class CommandHelp(Command):

    description = 'Display help message.'

    def execute(self, words):
        print(self.interface.help(), end='')


class MyShell(InteractiveInterface):

    welcome = 'An example Moco CLI program.\n'

    extend = {
        'hello': CommandHello,
        'parse': CommandParse,
        'help': CommandHelp,
    }


if __name__ == '__main__':
    my_shell = MyShell()
    my_shell.mainloop()
