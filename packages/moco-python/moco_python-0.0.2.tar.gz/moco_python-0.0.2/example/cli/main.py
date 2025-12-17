from moco import CommandLineInterface, Command, Parser, opt


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
        opt('--help', alias=['-h'], description='Show this help message.', is_help=True),
    ])

    def execute(self, words):
        args, opts = self.parser.parse(words)
        print(args)
        print(opts)


class MyCli(CommandLineInterface):

    description = 'An example Moco CLI program.'

    extend = {
        'hello': CommandHello,
        'parse': CommandParse,
    }

    parser = Parser([
        opt('--help', alias=['-h'], description='Show this help message.', is_help=True),
    ])

    def execute(self, words):
        _args, _opts = self.parser.parse(words)


if __name__ == '__main__':
    my_cli = MyCli()
    my_cli.launch()
