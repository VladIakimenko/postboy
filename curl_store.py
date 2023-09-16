import subprocess
import shlex
import json
import re
import os


class CurlStore:
    COMMANDS_FILE = 'postboy_data/commands.json'

    def __init__(self):
        self.commands = {}
        self.variables = {}
        self.grablist = []

        if os.path.exists(self.COMMANDS_FILE):
            with open(self.COMMANDS_FILE, 'r') as f:
                self.commands = json.load(f)

    def save_to_files(self):
        with open(self.COMMANDS_FILE, 'w') as f:
            json.dump(self.commands, f, indent=4)

    def save_command(self, name, command):
        command = command.replace('\\', '')
        command = ' '.join(command.split())
        self.commands[name] = command

    def delete_command(self, name):
        del self.commands[name]

    def save_variable(self, key, value):
        self.variables[key] = value

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

    def get_command(self, name):
        return self.commands.get(name, "")

    def list_commands(self):
        return sorted(list(self.commands.keys()))

    def check_missing_variables(self, command):
        placeholders = re.findall(r'{{(.*?)}}', command)
        missing = [placeholder for placeholder in placeholders if placeholder not in self.variables]
        return missing

    def execute_command(self, name):
        command = self.get_command(name)

        if not command.strip():
            return "Invalid command."

        missing_vars = self.check_missing_variables(command)
        while missing_vars:
            for var in missing_vars:
                value = input(f"Enter value for variable {{{{{var}}}}}: ")
                self.save_variable(var, value)
            missing_vars = self.check_missing_variables(command)

        for key, value in self.variables.items():
            command = command.replace("{{" + key + "}}", value)

        try:
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            return stdout.decode('utf-8') if process.returncode == 0 else stderr.decode('utf-8')
        except IndexError:
            return "Command could not be executed. Please check the saved command."

    def list_variables(self):
        return self.variables

    @staticmethod
    def verify_curl(curl_cmd):
        # add normal logic here
        return curl_cmd.strip().startswith("curl") and len(curl_cmd.strip()) > 0


