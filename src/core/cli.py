import os
import shlex
from time import sleep

import readline
import atexit

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from src.constants import TERMINAL_WIDTH, HISTORY_FILE

console = Console(force_terminal=True, width=TERMINAL_WIDTH)

# Load previous history
if os.path.exists(HISTORY_FILE):
    readline.read_history_file(HISTORY_FILE)
else:
    with open(HISTORY_FILE, 'w') as f:
        pass

# Save history on exit
atexit.register(readline.write_history_file, HISTORY_FILE)

# Set the spacing for the help text.
FIRST_COLUMN_WIDTH = 16
SECOND_COLUMN_WIDTH = 12


class CLI:
    def __init__(self):
        self.commands = {}

        self.global_options = [
            ("-h, --help", "Display help for the given command."),
        ]

    def command(self, name, arguments=None, keyword_args=None, help_text=""):
        """
        Register a command.
        :param name: command name
        :param arguments: List of tuples (arg_name, description)
        :param keyword_args: Dict like {'-n': ('name', 'desc', 'type'), '--name': ('name', 'desc', 'type')}
        :param help_text: Description of the command
        """
        def decorator(func):
            self.commands[name] = {
                "func": func,
                "args": arguments or [],
                "kwargs": keyword_args or {},
                "help": help_text
            }
            return func
        return decorator

    def start(self):
        console.print("[dim]Custom CLI[/dim]. Type 'help' to see available commands. Type 'exit' to quit.")
        while True:
            try:
                raw_input = input(">>> ").strip()
                if not raw_input:
                    continue
                else:
                    if readline.get_current_history_length() == 0 or readline.get_history_item(readline.get_current_history_length()) != raw_input:
                        readline.add_history(raw_input)

                if raw_input.lower() in ['exit', 'quit']:
                    with Live(console=console, transient=False) as live:
                        live.update(Spinner(name='dots', text="Shutting down...", style='yellow'))
                        sleep(2)
                        live.update(Text(f"Shutdown successfully!", style='yellow'))
                        break

                if raw_input.lower() == 'help':
                    self.print_help()
                    continue

                parts = shlex.split(raw_input)
                cmd_name = parts[0]
                args_and_kwargs = parts[1:]

                if cmd_name not in self.commands:
                    console.print(f"[red]'{cmd_name}' is not a recognized command.[/red]")
                    continue

                if len(args_and_kwargs) == 1 and args_and_kwargs[0] in ("-h", "--help"):
                    self.print_command_help(cmd_name)
                    continue

                cmd_info = self.commands[cmd_name]
                expected_args = cmd_info["args"]
                expected_kwargs = cmd_info["kwargs"]

                positional = []
                kwargs = {}
                i = 0

                while i < len(args_and_kwargs):
                    part = args_and_kwargs[i]
                    if part.startswith("-"):
                        if part not in expected_kwargs:
                            console.print(f"[red]Unknown keyword argument '{part}'[/red]")
                            break

                        key = expected_kwargs[part][0]  # canonical name
                        is_expecting_arg = True

                        for kwarg, cmd in expected_kwargs.items():
                            if key == kwarg.replace("-", ""):
                                is_expecting_arg = cmd[2] is not None

                        if is_expecting_arg and i + 1 >= len(args_and_kwargs):
                            console.print(f"[red]Missing value for keyword argument '{part}'[/red]")
                            break

                        value = args_and_kwargs[i + 1] if is_expecting_arg else None

                        if not value:
                            kwargs[key] = True
                            i += 1
                        elif not value.startswith("-"):
                            kwargs[key] = value
                            i += 2
                        else:
                            console.print(f"[red]Expected a value for '{part}' but got another flag.[/red]")
                    else:
                        positional.append(part)
                        i += 1

                if len(positional) != len(expected_args):
                    arg_list = ', '.join(name for name, _ in expected_args)
                    console.print(f"[red]'{cmd_name}' expects {len(expected_args)} positional arguments: {arg_list}[/red]")
                    continue

                cmd_info["func"](*positional, **kwargs)
            except Exception as e:
                console.print(f"[red]An error occurred:[/red] {e}")

    def print_help(self):
        console.print("[bold]Usage:[/bold]")
        console.print("    command [dim]<argument> <options>[/dim]", highlight=False, end="\n\n")

        if self.global_options:
            console.print("[bold]Options:[/bold]")
            options_table = Table(show_header=False, box=None, padding=(0, 1))
            options_table.add_column("Flag", style="blue", no_wrap=True, width=FIRST_COLUMN_WIDTH)
            options_table.add_column("Description")

            for flag, desc in self.global_options:
                options_table.add_row(flag, desc)

            console.print(options_table)
            console.print()

        console.print("[bold]Available commands:[/bold]")
        command_table = Table(show_header=False, box=None, padding=(0, 1))
        command_table.add_column("Command", style="blue", no_wrap=True, width=FIRST_COLUMN_WIDTH)
        command_table.add_column("Description")

        for name, cmd in self.commands.items():
            command_table.add_row(name, cmd["help"])

        console.print(command_table)

    def print_command_help(self, name):
        if name not in self.commands:
            console.print(f"[red]No such command: {name}[/red]")
            return

        cmd = self.commands[name]

        console.print(f"[bold]Description:[/bold]\n  {cmd['help']}", end="\n\n")

        args_part = " ".join(f"<{arg}>" for arg, _ in cmd["args"])
        console.print(f"[bold]Usage:[/bold]")
        console.print(f"    {name} {args_part}\n", highlight=False)

        if cmd["args"]:
            console.print("[bold]Arguments:[/bold]")
            arg_table = Table(show_header=False, box=None, padding=(0, 1))
            arg_table.add_column("Argument", style="blue", no_wrap=True, width=FIRST_COLUMN_WIDTH)
            arg_table.add_column("Description")

            for arg, desc in cmd["args"]:
                arg_table.add_row(arg, desc)

            console.print(arg_table)
            console.print()

        if cmd["kwargs"]:
            console.print("[bold]Options:[/bold]")

            # Group by canonical name
            kw_by_name = {}
            for k, (canonical, desc, value) in cmd["kwargs"].items():
                kw_by_name.setdefault(canonical, {"flags": [], "desc": desc, "type": value})["flags"].append(k)

            kw_table = Table(show_header=False, box=None, padding=(0, 1))
            kw_table.add_column("Flags", style="blue", no_wrap=True, width=FIRST_COLUMN_WIDTH)
            kw_table.add_column("Values", style="dim", no_wrap=True, width=SECOND_COLUMN_WIDTH, highlight=False)
            kw_table.add_column("Description")

            for kw_name, info in kw_by_name.items():
                flags = ", ".join(info["flags"])
                type_hint = f" <{info['type']}>" if info.get("type") else ""
                kw_table.add_row(flags, type_hint, info["desc"])

            console.print(kw_table)