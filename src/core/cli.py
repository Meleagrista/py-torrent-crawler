import shlex

from rich.console import Console
from rich.prompt import Prompt

console = Console(force_terminal=True)

class CustomPrompt(Prompt):
    prompt_suffix = ">>> "

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
        :param keyword_args: Dict like {'-n': ('name', 'desc'), '--name': ('name', 'desc')}
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
                raw_input = CustomPrompt.ask().strip()
                if not raw_input:
                    continue

                if raw_input.lower() in ['exit', 'quit']:
                    console.print("Exiting...")
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
                        if i + 1 >= len(args_and_kwargs):
                            console.print(f"[red]Missing value for keyword argument '{part}'[/red]")
                            break
                        if part not in expected_kwargs:
                            console.print(f"[red]Unknown keyword argument '{part}'[/red]")
                            break
                        key = expected_kwargs[part][0]  # canonical name
                        kwargs[key] = args_and_kwargs[i + 1]
                        i += 2
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
        console.print(f"[bold]Usage:[/bold]")
        console.print(f"{' '*4}command [options] [arguments]\n", markup=False)

        console.print("[bold]Options:[/bold]")
        for flag, desc in self.global_options:
            console.print(f"{' '*4}[blue]{flag:<20}[/blue] {desc}")
        console.print()

        console.print("[bold]Available commands:[/bold]")
        for name, cmd in self.commands.items():
            console.print(f"{' '*4}[blue]{name:<20}[/blue] {cmd['help']}")

    def print_command_help(self, name):
        if name not in self.commands:
            console.print(f"[red]No such command: {name}[/red]")
            return

        cmd = self.commands[name]

        console.print(f"[bold]Description:[/bold]\n  {cmd['help']}\n")

        args_part = " ".join(f"<{arg}>" for arg, _ in cmd["args"])
        console.print(f"[bold]Usage:[/bold]")
        console.print(f"{' '*4}{name} {args_part}\n", highlight=False)

        if cmd["args"]:
            console.print("[bold]Arguments:[/bold]")
            for arg, desc in cmd["args"]:
                console.print(f"{' '*4}[blue]{arg:<20}[/blue] {desc}")
            console.print()

        if cmd["kwargs"]:
            console.print("[bold]Options:[/bold]")

            # Group keyword args by canonical name
            kw_by_name = {}
            for k, (canonical, desc) in cmd["kwargs"].items():
                kw_by_name.setdefault(canonical, {"flags": [], "desc": desc})["flags"].append(k)

            for kw_name, info in kw_by_name.items():
                flags = ", ".join(info["flags"])
                console.print(f"{' '*4}[blue]{flags:<25}[/blue] {info['desc']}")