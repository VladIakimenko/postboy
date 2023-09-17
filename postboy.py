#!/usr/bin/env python3
import json
import readline
import shlex

from completers import CombinedCompleter, Completer
from curl_store import CurlStore


readline.parse_and_bind('tab: complete')
CURL_OPTIONS = ['add', 'list', 'view', 'change', 'delete', 'execute']
VAR_OPTIONS = ['variables', 'set', 'grab']
COMMON_OPTIONS = ['quit']
OPTIONS = CURL_OPTIONS + VAR_OPTIONS + COMMON_OPTIONS


def multiline_input(prompt):
    lines = []
    print(prompt)
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return '\n'.join(lines)


def process_response(response):
    try:
        parsed_response = json.loads(response)
        print(f"\n{json.dumps(parsed_response, ensure_ascii=False, indent=4)}\n")
        saved_vars = store.grab_from_response(parsed_response)
        if saved_vars:
            print(f"{', '.join(saved_vars)} saved from response.")
    except json.JSONDecodeError:
        print(f"\n{response}\n")


def format_curl(command: str) -> str:
    parts = shlex.split(command)

    formatted_command = []
    skip_next = False

    for i, part in enumerate(parts):
        if skip_next:
            skip_next = False
            continue

        if part == '-H':
            formatted_command.append(f"{part} {parts[i + 1]}")
            skip_next = True
        elif part == '-d':
            formatted_command.append(part)
            formatted_command.append(json.dumps(json.loads(parts[i + 1]), ensure_ascii=False, indent=4))
            skip_next = True
        else:
            formatted_command.append(part)

    formatted_command_str = ' '.join(formatted_command[:3])
    formatted_command_str += '\n' + '\n'.join(formatted_command[3:])

    return formatted_command_str


if __name__ == "__main__":
    store = CurlStore()

    curl_commands = store.list_commands()
    variables = store.list_variables()

    curl_completer = Completer(store.list_commands())
    variable_completer = Completer(store.list_variables())

    mapping = {
        **{option: curl_commands for option in CURL_OPTIONS},
        **{option: variables for option in VAR_OPTIONS}
    }
    main_completer = CombinedCompleter(
        option_to_args_mapping=mapping,
        no_arg_options=COMMON_OPTIONS,
        all_options=OPTIONS + curl_commands,
    )

    while True:
        try:
            readline.set_completer(main_completer.complete)
            input_ = input("> ").rstrip().replace(',', ' ').split()
            choice, args = input_[0], input_[1:]

            if choice in OPTIONS:
                if choice == "add":
                    if not args:
                        args.append(input("Enter a name for the command to add: "))
                    for name in args:
                        command = multiline_input(f"Enter your curl command for {name} (double enter to submit): ")
                        if store.verify_curl(command):
                            store.save_command(name, command)
                            print(f"Curl command saved under name: '{name}'.")
                        else:
                            print("Invalid curl command.")

                elif choice == "view":
                    if not args:
                        readline.set_completer(curl_completer.complete)
                        input("Enter the name of the command to view: ")
                    for name in args:
                        if name in store.list_commands():
                            curl = format_curl(store.get_command(name))
                            print(f"\n{curl}\n")
                        else:
                            print(f"No command found with the name: {name}.")

                elif choice == "list":
                    commands = store.list_commands()
                    if commands:
                        print()
                        for cmd in commands:
                            print(cmd)
                        print()
                    else:
                        print("No commands saved yet.")

                elif choice == "change":
                    if not args:
                        readline.set_completer(curl_completer.complete)
                        args.append(input("Enter the name of the command to modify: "))
                    for name in args:
                        if name in store.list_commands():
                            current_command = store.get_command(name)
                            print(f"Current curl for {name}:")
                            print(f"\n{current_command}\n")
                            new_command = multiline_input(
                                f"Enter the new curl command for {name} (double enter to submit): "
                            )
                            if store.verify_curl(new_command):
                                store.save_command(name, new_command)
                                print(f"Curl command {name} has been updated.")
                            else:
                                print("Invalid curl command.")
                        else:
                            print(f"No command found with the name: {name}.")

                elif choice == "delete":
                    if not args:
                        readline.set_completer(curl_completer.complete)
                        args.append(input("Enter the name of the command to delete: "))
                    for name in args:
                        if name in store.list_commands():
                            store.delete_command(name)
                            print(f"Curl command {name} has been deleted.")
                        else:
                            print(f"No command found with the name: {name}.")

                elif choice == "execute":
                    if not args:
                        readline.set_completer(curl_completer.complete)
                        args.append(input("Enter the name of the command to execute: "))
                    for name in args:
                        response = store.execute_command(name)
                        process_response(response)

                elif choice == "variables":
                    variables = store.list_variables()
                    if variables:
                        print()
                        for key, value in variables.items():
                            print(f"{key}: '{value}'")
                        print()
                    else:
                        print("No variables saved yet.")

                elif choice == "set":
                    if not args:
                        readline.set_completer(variable_completer.complete)
                        args.append(input("Enter the name of the variable to set: "))
                    for var_name in args:
                        readline.set_completer(None)
                        new_value = input(f"Enter the value for '{var_name}': ")
                        store.save_variable(var_name, new_value)
                        if var_name in store.grablist:
                            store.grablist.remove(var_name)
                        print(f"'{var_name}' saved.")

                elif choice == "grab":
                    if not args:
                        readline.set_completer(variable_completer.complete)
                        args.append(input("Enter the name of the variable to grab from responses: "))
                    for var_name in args:
                        store.grablist.append(var_name)
                        print(f"'{var_name}' is set to be extracted from responses.")

                elif choice == "quit":
                    for key, value in store.commands.items():
                        value = ' '.join(value.split())
                        value = value.replace('\\', '')
                        store.commands[key] = value
                    store.save_to_files()
                    print("Data saved. Any key to exit.")
                    input()
                    break

            elif choice == "":
                continue

            elif choice in store.list_commands():
                response = store.execute_command(choice)
                process_response(response)

            else:
                print("\n" + "\n".join(OPTIONS) + "\n")

        except KeyboardInterrupt:
            print("\n")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            