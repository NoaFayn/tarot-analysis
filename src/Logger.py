from rich.console import Console

class Logger(object):
    def __init__(self, verbosity=0, quiet=False):
        self.verbosity = verbosity
        self.quiet = quiet
        self.console = Console()

    def debug(self, message):
        if self.verbosity >= 2:
            self.console.print("{}[DEBUG]{} {}".format("[yellow3]", "[/yellow3]", message), highlight=False)

    def verbose(self, message):
        if self.verbosity >= 1:
            self.console.print("{}[VERBOSE]{} {}".format("[blue]", "[/blue]", message), highlight=False)

    def info(self, message):
        if not self.quiet:
            self.console.print("{}[*]{} {}".format("[bold blue]", "[/bold blue]", message), highlight=False)

    def success(self, message):
        if not self.quiet:
            self.console.print("{}[+]{} {}".format("[bold green]", "[/bold green]", message), highlight=False)

    def warning(self, message):
        if not self.quiet:
            self.console.print("{}[-]{} {}".format("[bold orange3]", "[/bold orange3]", message), highlight=False)

    def error(self, message):
        if not self.quiet:
            self.console.print("{}[!]{} {}".format("[bold red]", "[/bold red]", message), highlight=False)
