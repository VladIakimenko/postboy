import json
import os
import re
import shlex
import subprocess


class CurlStore:
    commands_file = "postboy_data/commands.json"

    def __init__(self):
        self.commands = {}
        self.variables = {}
        self.grablist = []

        if os.path.exists(self.commands_file):
            with open(self.commands_file, "r") as f:
                self.commands = json.load(f)

    def save_to_files(self):
        dir_path = os.path.split(self.commands_file)[0]
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.commands_file, "w") as f:
            json.dump(self.commands, f, indent=4, ensure_ascii=False)

    def save_command(self, name, command):
        command = command.replace("\\", "")
        command = " ".join(command.split())
        command = self.strip_hack(command)
        self.commands[name] = command

    def delete_command(self, name):
        del self.commands[name]

    def set_variable(self, key, value):
        self.variables[key] = value
        return f"{key}: '{value}'"

    def grab_from_response(self, parsed_response: dict) -> list[str]:
        saved_variables = []
        for key in self.grablist:
            if key in parsed_response:
                self.variables[key] = parsed_response[key]
                saved_variables.append(key)
        return saved_variables

    def list_commands(self):
        return sorted(list(self.commands.keys()))

    def check_missing_variables(self, command):
        placeholders = re.findall(r"{{(.*?)}}", command)
        missing = [
            placeholder
            for placeholder in placeholders
            if placeholder not in self.variables
        ]
        return missing

    def execute_command(self, name):
        command = self.commands.get(name)

        if command is None:
            return "Invalid command."

        missing_vars = self.check_missing_variables(command)
        while missing_vars:
            for var in missing_vars:
                value = input(f"Enter value for variable '{var}': ")
                self.set_variable(var, value)
            missing_vars = self.check_missing_variables(command)

        for key, value in self.variables.items():
            command = command.replace("{{" + key + "}}", value)

        try:
            process = subprocess.Popen(
                shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            return (
                stdout.decode("utf-8")
                if process.returncode == 0
                else stderr.decode("utf-8")
            )
        except IndexError:
            return "Command could not be executed. Please check the saved command."

    def list_variables(self):
        return self.variables

    @staticmethod
    def verify_curl(curl_cmd):
        curl_cmd = curl_cmd.strip()

        if not curl_cmd.startswith("curl"):
            return False, "The command must start with 'curl'."

        parts = shlex.split(curl_cmd)

        if len(parts) < 3:
            return False, "The command is incomplete."

        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

        if parts[1].startswith('-') or re.match(r'http[s]?://', parts[1], re.IGNORECASE):
            return False, "An HTTP method must be explicitly stated (even if it is GET)."
        elif parts[1].upper() not in http_methods:
            return False, f"'{parts[1]}' is not a recognized HTTP method."

        url_part_exists = any(re.match(r'http[s]?://', part, re.IGNORECASE) for part in parts[2:])
        if not url_part_exists:
            return False, "A valid URL must be provided."

        for i, part in enumerate(parts):
            if part in ("-H", "-F", "-d") and (i == len(parts) - 1 or parts[i + 1].startswith('-')):
                return False, f"The option '{part}' must have an accompanying value."

        return True, ''

    @staticmethod
    def strip_hack(command):
        undesirable_map = {
            "{ ": "{",
            "} ": "}",
            "[ ": "[",
            "] ": "]",
        }
        for key, value in undesirable_map.items():
            while key in command:
                command = command.replace(key, value)
        return command


