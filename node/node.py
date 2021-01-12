import re
from .terminal import Terminal, Command


class Node:
    def __init__(self):
        commands = self.node_commands()
        self.terminal = Terminal(commands)

    def start(self):
        while True:
            command = self.terminal.get_input()
            self.run_command(command)

    def upload(self, file_name: str):
        pass

    def download(self):
        pass

    def search(self, file_name: str):
        pass

    def run_command(self, command: str):
        command_parts = command.split()
        if 'upload' in command:
            file_name = command_parts[3].replace('"', '')
            self.upload(file_name)
        if 'download' in command:
            self.download()
        if 'search' in command:
            file_name = command_parts[2].replace('"', '')
            self.search(file_name)

    @staticmethod
    def node_commands() -> Command:
        file_name_re = r'\w*(\.\w*)?'
        commands = list()
        commands.append(
            re.compile(fr'\Atorrent -setMode upload "{file_name_re}"$')
        )
        commands.append(
            re.compile(r'\Atorrent -setMode download$')
        )
        commands.append(
            re.compile(fr'\Atorrent -search "{file_name_re}"$')
        )
        return commands
