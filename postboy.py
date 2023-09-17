#!/usr/bin/env python3
import json
import readline
import shlex

from completers import CombinedCompleter, Completer
from curl_store import CurlStore

readline.parse_and_bind("tab: complete")
CURL_OPTIONS = ["add", "list", "view", "change", "delete", "execute"]
VAR_OPTIONS = ["variables", "set", "grab"]
COMMON_OPTIONS = ["quit"]


def multiline_input(prompt):
    lines = []
    print(prompt)
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return "\n".join(lines)


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

        if part == "-H":
            formatted_command.append(f"{part} {parts[i + 1]}")
            skip_next = True
        elif part == "-d":
            formatted_command.append(part)
            formatted_command.append(
                json.dumps(json.loads(parts[i + 1]), ensure_ascii=False, indent=4)
            )
            skip_next = True
        else:
            formatted_command.append(part)

    formatted_command_str = " ".join(formatted_command[:3])
    formatted_command_str += "\n" + "\n".join(formatted_command[3:])

    return formatted_command_str


def process_curl_option(command: str, requested_curls: list):
    if not requested_curls and command != "list":
        completer = curl_completer if command not in "add" else None
        readline.set_completer(completer.complete)
        requested_curls.append(
            input(f"{command.capitalize()}ing curl command. Enter name: ")
        )

    def list_curls():
        all_curls = store.list_commands()
        if all_curls:
            print()
            for curl_name in all_curls:
                print(curl_name)
            print()
        else:
            print("No curls saved yet.")

    def add_curl():
        curl = multiline_input(
            f"Enter your curl command for {name} (double enter to submit): "
        )
        if store.verify_curl(curl):
            store.save_command(name, curl)
            print(f"Curl command saved under name: '{name}'.")
        else:
            print("Invalid curl command.")

    def view_curl():
        curl = format_curl(store.commands.get(name))
        print(f"\n{curl}\n")

    def change_curl():
        current_command = store.commands.get(name, "")
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

    def delete_curl():
        store.delete_command(name)
        print(f"Curl command {name} has been deleted.")

    def execute_curl():
        response = store.execute_command(choice)
        process_response(response)

    name_specific_commands_map = {
        "add": add_curl,
        "view": view_curl,
        "change": change_curl,
        "delete": delete_curl,
        "execute": execute_curl,
    }

    if command == "list":
        list_curls()
    else:
        for name in requested_curls:
            if name not in store.list_commands() and command != "add":
                print(f"No command found with the name: '{name}'.")
                continue
            name_specific_commands_map[command]()


def process_variable_option(command: str, requested_variables: list):
    if "*" in requested_variables:
        requested_variables = list(store.variables.keys())

    if not requested_variables and command != "variables":
        completer = variable_completer
        readline.set_completer(completer.complete)
        requested_variables.append(
            input(f"Enter the name of the variable to {command}: ")
        )

    def list_vars():
        variables = store.list_variables()
        if variables:
            print()
            for key, value in variables.items():
                print(f"{key}: '{value}'")
            print()
        else:
            print("No variables saved yet.")

    def set_var():
        readline.set_completer(None)
        new_value = input(f"Enter the value for '{var_name}': ")
        store.set_variable(var_name, new_value)
        if var_name in store.grablist:
            store.grablist.remove(var_name)
        print(f"'{var_name}' saved.")

    def grab_var():
        store.grablist.append(var_name)
        print(f"'{var_name}' is set to be extracted from responses.")

    name_specific_commands_map = {
        "set": set_var,
        "grab": grab_var,
    }

    if command == "variables":
        list_vars()
    else:
        for var_name in requested_variables:
            name_specific_commands_map[command]()


if __name__ == "__main__":
    store = CurlStore()

    curl_commands = store.list_commands()
    variables = store.list_variables()

    curl_completer = Completer(store.list_commands())
    variable_completer = Completer(store.list_variables())

    mapping = {
        **{option: curl_commands for option in CURL_OPTIONS},
        **{option: variables for option in VAR_OPTIONS},
    }
    main_completer = CombinedCompleter(
        option_to_args_mapping=mapping,
        no_arg_options=COMMON_OPTIONS,
        all_options=CURL_OPTIONS + VAR_OPTIONS + COMMON_OPTIONS + curl_commands,
    )

    while True:
        try:
            readline.set_completer(main_completer.complete)
            input_ = input("> ").rstrip().replace(",", " ").split()
            if input_:
                choice, args = input_[0], input_[1:]

                if choice in CURL_OPTIONS:
                    process_curl_option(choice, args)

                elif choice in VAR_OPTIONS:
                    process_variable_option(choice, args)

                elif choice == "quit":
                    for key, value in store.commands.items():
                        value = " ".join(value.split())
                        value = value.replace("\\", "")
                        store.commands[key] = value
                    store.save_to_files()
                    print("Data saved. Any key to exit.")
                    input()
                    break

                elif choice in store.list_commands():
                    response = store.execute_command(choice)
                    process_response(response)

                else:
                    print(
                        "\n"
                        + "\n".join(CURL_OPTIONS + VAR_OPTIONS + COMMON_OPTIONS)
                        + "\n"
                    )

            else:
                continue

        except KeyboardInterrupt:
            print("\n")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
