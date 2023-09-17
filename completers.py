import readline


class Completer:
    """
    Basic completer.
    Usage:
    completer = Completer(options)
    readline.set_completer(completer.complete)
    """

    def __init__(self, options):
        self.options = options

    def complete(self, text, state):
        matches = [option for option in self.options if option.startswith(text)]
        if state < len(matches):
            return matches[state]


class CombinedCompleter(Completer):
    def __init__(
        self,
        option_to_args_mapping: dict,
        no_arg_options: list,
        all_options: list = None,
    ):
        """
        option_to_args_mapping: Dictionary mapping an option to its potential arguments.
        no_arg_options: List of options that don't expect further arguments.
        all_options: List of all options.
                     If not provided, it's generated from option_to_args_mapping and no_arg_options.
        """
        self.option_to_args_mapping = option_to_args_mapping
        self.no_arg_options = no_arg_options

        if all_options is None:
            all_options = list(option_to_args_mapping.keys()) + no_arg_options
        else:
            self.all_options = all_options

        super().__init__(options=all_options)

    def get_args_for_option(self, option):
        return self.option_to_args_mapping.get(option, [])

    def complete(self, text, state):
        buffer = readline.get_line_buffer().strip()
        tokens = buffer.split()

        if not tokens:
            self.options = self.all_options
        elif len(tokens) == 1:
            if tokens[0] in self.no_arg_options:
                self.options = []
            else:
                potential_args = self.get_args_for_option(tokens[0])
                if potential_args:
                    self.options = potential_args
                else:
                    self.options = self.all_options
        else:
            self.options = self.get_args_for_option(tokens[0])

        return super().complete(text, state)
