#!/usr/bin/env python3
import json
import readline
import shlex

from curl_store import CurlStore


readline.parse_and_bind('tab: complete')
OPTIONS = ['add', 'list', 'view', 'change', 'delete', 'execute', 'variables', 'set', 'grab', 'quit']

# accept arguments after main menu commands


def main_completer(text, state):    # Turn into classes and realize inheritance
    options = OPTIONS + store.list_commands()
    matches = [i for i in options if i.startswith(text)]
    if state < len(matches):
        return matches[state]
    return None


def curl_completer(text, state):
    options = store.list_commands()
    matches = [i for i in options if i.startswith(text)]
    if state < len(matches):
        return matches[state]
    return None


def variable_completer(text, state):
    options = store.list_variables()
    matches = [i for i in options if i.startswith(text)]
    if state < len(matches):
        return matches[state]
    return None


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

    while True:
        try:
            readline.set_completer(main_completer)
            choice = input("> ").rstrip()

            if choice in OPTIONS:                       # consider dict-mapped menu
                if choice == "add":
                    name = input("Enter a name for the command: ")
                    command = multiline_input("Enter your curl command (double enter to submit): ")

                    if store.verify_curl(command):
                        store.save_command(name, command)
                        print(f"Curl command saved under name: '{name}'.")
                    else:
                        print("Invalid curl command.")

                elif choice == "view":
                    readline.set_completer(curl_completer)
                    name = input("Enter the name of the command: ")
                    curl = format_curl(store.get_command(name))
                    print(f"\n{curl}\n")

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
                    readline.set_completer(curl_completer)
                    name = input("Enter the name of the command to modify: ")

                    if name in store.list_commands():
                        current_command = store.get_command(name)
                        print(f"Current curl for {name}:")
                        print(f"\n{current_command}\n")
                        new_command = multiline_input("Enter the new curl command (double enter to submit): ")
                        if store.verify_curl(new_command):
                            store.save_command(name, new_command)
                            print(f"Curl command {name} has been updated.")
                        else:
                            print("Invalid curl command.")
                    else:
                        print(f"No command found with the name: {name}.")

                elif choice == "delete":
                    readline.set_completer(curl_completer)
                    name = input("Enter the name of the command to delete: ")
                    if name in store.list_commands():
                        store.delete_command(name)
                        print(f"Curl command {name} has been deleted.")
                    else:
                        print(f"No command found with the name: {name}.")

                elif choice == "execute":
                    readline.set_completer(curl_completer)
                    name = input("Enter the name of the command: ")
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
                    readline.set_completer(variable_completer)
                    var_name = input("Enter the name of the variable to set: ")
                    readline.set_completer(None)
                    new_value = input(f"Enter the value for '{var_name}': ")
                    store.save_variable(var_name, new_value)
                    if var_name in store.grablist:
                        store.grablist.remove(var_name)
                    print(f"'{var_name}' saved.")

                elif choice == "grab":
                    readline.set_completer(variable_completer)
                    var_name = input("Enter the name of the variable to grab from responses: ")
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