# Postboy

A terminal based, customizable API client, that uses '*curls*' (CURL syntax-based http requests) to interact with an 
API.   
It is capable of automatic saving of data from responses to variables to be further re-used in requests. 
This together with other handy instruments streamlines the process of API development, testing and maintenance in environments where the 
use of graphical API clients is not desirable.

# Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [General](#general)
  - [Operations with curls](#operations-with-curls)
  - [Operations with variables](#operations-with-variables)
- [Contributing](#contributing)
- [License](#license)

# Introduction

The application is an API client that is fully operational in environments, where no GUI interface is available.
Postboy is a lightweight command line instrument, that finely operates even with X-server down, yet providing all
necessary tools for interaction with an API in a comfortable reusable manner.  
In order to use the app, one should be acquainted with the CURL syntax, since it is entirely based on it.
The application saves CURL syntax-based http requests (here and further will be mentioned as '***curls***') to 
the store under user-specified names, those can later be used for sending requests to an API.   
The application expects json responses from the server and displays them in a nice structured manner straight in 
the terminal.  
The requests may include dynamic values, read from variables. These values should be included to curls 
as placeholders enclosed in '{{*variable_name*}}'. The application provides means to manage these variables, store, set 
and change their values. It can as well be adjusted to anticipate specific keys in the server responses, and save the
values of those keys to a variable.  
The application may be helpful to backend developers, software testers and QA specialists, who require to interact 
with an API in a terminal-based environment. 

# Features

- No GUI
- Saves requests in CURL syntax under user-specified names
- Sends corresponding requests, when previously saved curls are addressed to by their names
- Supports placeholders in curls 
(searches for a corresponding variable in the store and prompts to enter a value, if absent)
- Can be adjusted to automatically update variables' values, if present in response
- Possesses a user-friendly, simple and intuitive interface, requires no special knowledge after the curls have been
saved to the store
- Supports both, the direct curl storage editing as a json file, as well as the use of built-in methods to manage curls
- Flexible syntax including the use of commands with arguments in one line, commands without arguments 
(arguments are prompted to be entered on a new line), arguments directly without a command (in certain cases), etc... 

# Installation

Clone the repository:
```bash

git clone https://github.com/VladIakimenko/postboy.git
```
Engage the virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```
Install the necessary packages:
```bash
pip install -r postboy/requirements.txt
```
**Optional steps:**  
Make the script executable 
(this step ensures the script is executable, even if GIT did not preserve the executable bit):
```bash
chmod +x postboy/postboy.py
```
Add a symbolic link for the app to '*/usr/local/bin*' to allow execution from anywhere:
```bash
sudo ln -s $(pwd)/postboy/postboy.py /usr/local/bin/postboy
```
**Launch:**  
The app is launched with `python postboy/postboy.py`

**NOTE:** In order to use the symbolic link and run the app with the `postboy` command from any directory,
the packages from the '*requirements.txt*' should be installed system-wide (not within the virtual environment). 
To do so, skip the '*Engage the virtual environment*' step.  
When the application quits, it saves the store data to a file at *postboy_data/commands.json*. 
It uses a relative path for the file location, which means, that if you launch the application from the installation 
folder, it will use the *postboy_data/commands.json* located inside this very directory.  
When you launch the application from elsewhere, the folder will be created in the catalogue from which the `postboy` 
command was executed. This allows the usage of different data files for different APIs, avoiding extensively 
massive curl libraries and troubles caused with curl names crossing.


# Usage

## General

`> ` - anticipating the command input  
`any input` - list available commands  
`tab` - auto complete input  
`double tab` - list all available input options (considering what has already been entered)  
`ctrl + c` - cancel input, back to main  

### quit
The command is used to safely exit the application. The changes introduced to the curls store will be saved to the 
library file at *postboy_data/commands.json* at this stage. To quit and discard the changes you can use `ctrl + z`.  
NOTE: All newly added or edited curls will be lost in case the application is exited otherwise than with the `quit` 
command. This is done purposely to allow discarding the changes in case the library was messed up. Please consider this
peculiarity.

## Operations with curls

### add [curl_name]
[...] - optional argument (input without brackets)  
Adds a new curl request to the store. In case the argument is not provided, will prompt for the name of the curl. 
Multiline input is supported. To end the input use the '*return*' key twice.  

***Recommendation:*** Use consistent names for the curls. The name could hold the requested action (maybe based on the 
CRUDL principles) and the object(s) of action. 
This would considerably simplify the work with the application when loads of curls have been saved. 
If you use the same curl library (*postboy_data/commands.json*) for multiple projects, 
include a prefix or postfix denoting the project or API name.  
A good name could look somewhat like '*aws_auth_user*', '*ya_upload_file*' or '*vk_update_profile_photo*'

***Curls***  
The requests syntax is designed in a way, that makes any request work fine directly in most linux 
terminals, even if Postboy is not installed. So any command may simply be copied (for example from the output of the 
`view` command) and used directly in bash or other terminal emulator.
The requests must follow the syntax below (replace <...> accordingly):  

basic:
```
curl -X <method> \
-H '<header_name>: <header_value>' \
<api_endpoint>
```

json payload:
```
curl -X <method> \
-H '<header_name>: <header_value>' \
-d '{
    "key1": "value1",
    "key2": "value2"
}' \
<api_endpoint>
```

form-data:
```
curl -X <method> \
-H '<header_name>: <header_value>' \
-F 'payload={
    "key1": "value1",
    "key2": "value2"
}' \
-F '<file_field_name>=@<file_path>' \
<api_endpoint>
```
NOTES:
- The method is compulsory to be stated explicitly (even if it is **GET**, the method part should never be omitted)
- The **-H** (header) section is optional, but if present must immediately follow the method line
- Be precise with the quotes. They must be used exactly as in samples, single quotes after the flag, double quotes in 
json payload
- API Endpoint is stated as per the following example: '*http://127.0.0.1:8000/api/auth/send-code/*'
- One-line input is also acceptable: `curl -X <method> -H '<header_name>: <header_value>' <api_endpoint>`
- File path for the form-data requests supports both relative (from where Postboy has been started) and absolute paths

### list
This command takes no arguments.  
Displays the list of all curls available in the store. At launch Postboy loads the curls from 
*postboy_data/commands.json*. If no commands have been saved yet, will display the message accordingly. Curls are added
with the `add` command and are saved to a file, when quitting the application.

### view [curl_name]
[...] - optional argument (input without brackets)  
Displays the curl command saved under the name '*curl_name*'. The curl is displayed in multi-line format, which the 
application accepts. This means that in order to make a new command out of an existing one, you can copy-paste the 
output of the view command to a notepad, edit as per your requirements and paste it to the `add` command. Postboy 
will gladly accept the syntax.  
If several arguments given, the application will chain up the outputs.

### change [curl_name]
[...] - optional argument (input without brackets)  
Prints out the curl saved under the name '*curl_name*' in a single-line syntax and opens the multiline input (same as in
the `add` command).
After the new curl is provided, substitutes the '*curl_name*' record in the store.

### delete [curl_name]
[...] - optional argument (input without brackets)  
Deletes the curl saved under the name '*curl_name*' from the store. The changes will be reflected in the 
*postboy_data/commands.json* only after the `quit` command is executed.

### execute [curl_name]
[...] - optional argument (input without brackets)  
Executes the curl saved under the name '*curl_name*'. The command is fully equivalent to entering the name of the curl
directly. This means that `execute auth_user` would result in exactly the same as simply `auth_user`.

## Operations with variables
Variables serve as a mean to incorporate dynamic content into requests by replacing placeholders formatted as 
'*{{var_name}}*'. A common scenario involves a request carrying a payload that requires a value previously returned 
by the server in an earlier response. Here, we assign the value to a variable, which is used
to replace the placeholder with the corresponding name. For example, variables are frequently used to insert an access 
token, which was obtained from a prior response, into the request header to avoid copy-pasting it every time.

***Placeholders***  
The application supports placeholders in the curl commands enclosed in '*{{variable_name}}*'. If the curl is saved 
with a placeholder, the application (when executing such a curl) will search for a variable with a corresponding name 
in the store, and if present, use its value instead of the placeholder. Otherwise, it will request the user to input 
the value for this particular placeholder everytime the curl is executed.  
The operations available over the variables are described below in the corresponding section.
```
curl -X GET \
-H 'Authorization: Bearer {{access_token}}' \
http://127.0.0.1:8000/api/users/
```

This curl will search for a variable with the name '*access_token*'.  

The variables may be both `set` manually or updated from responses every time it contains a key, corresponding 
to the variable name. You can adjust the application to 'listen' for a specific key with the `grab` command. When 
you later manually `set` a variable which is being listened to, it will stop being updated from responses and use the 
value that was manually established.

### set [var_name]
[...] - optional argument (input without brackets)  
Manually assign a specific value to a variable. In case the argument is not provided, will prompt for the variable's 
name. The value should be entered on the next line (when requested). If the variable exists, the app will change its 
value. Otherwise, a variable with the given name will be created and the value will be assigned.

NOTE: Setting a variable removes it from the list of automatically updated variables formed by the `grab` command.

### variables
This command takes no arguments.  
Displays the list of all currently saved variables and their values. If no variables have been saved yet, will display 
the message accordingly.  
Variables are not saved between the sessions, so the lifetime of a variable is only until the application is 
closed.

### grab [var_name]
Adds a variable to the 'listening' list. The variables added with the `grab` command update their values each time 
a response contains a key corresponding to the name of the variable. Well supports chaining the variable names in one 
line, like `grab access_token refresh_token user_id`.

In order to remove a variable from the listening list, you can `set` a specific value to this variable.

### unset [var_name]
Removes the variable from the store entirely (both the key and the value).


# Contributing
Contributions of all forms are welcomed. 
Whether you're fixing a bug, adding a new feature, or improving documentation, your help is appreciated.

### How to Contribute
**Report Bugs:** If you encounter a bug, please send a detailed report to [v_yakimenko@inbox.ru](mailto:v_yakimenko@inbox.ru). 
Include steps to reproduce the bug, the expected outcome, and the actual outcome.

**Suggest Enhancements:** Check out the [issues.md](issues.md) file for a list of planned improvements. 
If you have an idea for enhancing the project that's not listed, feel free to suggest it by sending an email or 
opening an issue on the project's issue tracker.

**Tackle Existing Issues:** Feel free to take on any of the improvements or bug fixes listed in the issues.md file. 
If you decide to work on an issue, please indicate this by sending an email to [v_yakimenko@inbox.ru](mailto:v_yakimenko@inbox.ru) 
to avoid duplicate efforts.

**Submit Pull Requests:** If you've developed a fix or an enhancement, submit a pull request with your changes. 
Ensure your code adheres to the existing style of the project to maintain consistency.

### Pull Request Process
- Fork the repository and create your branch from master.
- Update the README.md, if applicable.
- Submit a pull request to the original repository.

# License
This project is licensed under the Apache License 2.0. 
This means that you can freely use, modify, distribute, and contribute back to the project under the terms of this 
license.

For more details, please see the [LICENSE](LICENSE) file included with this project.