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


# class CombinedCompleter(Completer):
#     """
#     Complex logic completer.
#     Extends the Completer to correctly suggest arguments depending on the entered command.
#     cmd_options - options that are followed by curl commands
#     var_options - options that are followed by variable names
#     common_options - options that take no arguments
#     curls - the list of curl names available as arguments
#     variables - the list of variable names available as arguments
#     """
#     def __init__(self, cmd_options, var_options, common_options, curls, variables):
#         self.cmd_options = cmd_options
#         self.var_options = var_options
#         self.common_options = common_options
#
#         self.curls = curls
#         self.variables = variables
#
#         super().__init__(options=cmd_options + var_options + common_options + self.curls)
#
#     def get_options_based_on_cmd(self, cmd):
#         if cmd in self.cmd_options:
#             return self.curls
#         else:
#             return self.variables
#
#     def complete(self, text, state):
#         buffer = readline.get_line_buffer().strip()
#         tokens = buffer.split()
#         all_options = self.cmd_options + self.var_options + self.common_options
#
#         if not tokens or (len(tokens) == 1 and tokens[0] not in all_options):
#             self.options = all_options + self.curls
#         else:
#             self.options = self.get_options_based_on_cmd(tokens[0])
#
#         return super().complete(text, state)

class CombinedCompleter(Completer):
    def __init__(self, option_to_args_mapping: dict, no_arg_options: list, all_options: list = None):
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
            # If only one token, it might be the start of an option or an argument
            if tokens[0] in self.no_arg_options:
                self.options = []
            else:
                potential_args = self.get_args_for_option(tokens[0])
                if potential_args:
                    self.options = potential_args
                else:
                    self.options = self.all_options
        else:
            # For more than one token, assume the first token is an option
            # and suggest arguments for it
            self.options = self.get_args_for_option(tokens[0])

        return super().complete(text, state)
