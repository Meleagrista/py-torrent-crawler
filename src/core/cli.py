import shlex


class CLI:
    def __init__(self):
        self.commands = {}

    def command(self, name, arguments=None, help_text=""):
        """
        Decorator to register a command.
        :param name: command name
        :param arguments: List of argument names (strings)
        :param help_text: description/help text
        """
        def decorator(func):
            self.commands[name] = {
                "func": func,
                "args": arguments or [],
                "help": help_text
            }
            return func
        return decorator

    def start(self):
        print("Custom CLI. Type 'help' to see available commands. Type 'exit' to quit.")
        while True:
            try:
                raw_input = input(">>> ").strip()
                if not raw_input:
                    continue

                if raw_input.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break

                if raw_input.lower() == 'help':
                    self.print_help()
                    continue

                # Use shlex.split to properly handle quoted arguments
                parts = shlex.split(raw_input)
                cmd_name = parts[0]
                args = parts[1:]

                if cmd_name in self.commands:
                    cmd_info = self.commands[cmd_name]
                    expected_args = cmd_info["args"]

                    if len(args) != len(expected_args):
                        print(f"Error: '{cmd_name}' expects {len(expected_args)} arguments: {', '.join(expected_args)}")
                        continue

                    cmd_info["func"](*args)
                else:
                    print(f"'{cmd_name}' is not a recognized command. Type 'help' to see available commands.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def print_help(self):
        print("Available commands:")
        for name, cmd in self.commands.items():
            args = ' '.join(f"<{arg}>" for arg in cmd['args'])
            print(f"  {name} {args}\n    {cmd['help']}")