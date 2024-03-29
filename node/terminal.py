import re
from typing import List

Command = List[re.Pattern]


class Terminal:
    def __init__(self, commands: Command):
        self.commands = commands

    def get_input(self) -> str:
        input_command = input('Enter your command.\n')
        for command in self.commands:
            match = command.match(input_command)
            if match:
                return input_command
