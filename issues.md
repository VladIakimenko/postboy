1. **Add 'grab *{{key_in_response}}* from *{{curl_name}}* as *{{var_name_to_save}}*' functionality**

It seems helpful to open a possibility of having a variable grabbed from server responses to be saved under a different name. 

For the moment, when we use, for example,  the ```grab user_id``` command, the app will search for the '*user_id*' key in response jsons
and, in case one is found, save its value to a variable under the '*user_id*' name. This means that the placeholders in the curls
should obligatory look like '*{{user_id}}*'. 

Though sometimes that may be an obstacle.  
For instance, if a single request holds the ids of 2 different user roles at the same time, we would have to use a specific name for
each of the placeholders (somewhat like '*{{admin_id}}*' and '*{{client_id}}*' instead of the '*{{user_id}}*').  
But in case the server returns both of these ids under the same '*user_id*' key, in the current implementation we would have to copy-paste the 
values to the ```set admin_id``` and ```set client_id``` commands respectively. 

The desired behaviour is to allow the use of the following commands:
```
grab user_id from get_admin as admin_id
grab user_id from get_client as client_id
```
where '*get_admin*' and '*get_client*' are the names of the curls (the server returns the corresponding ids under the '*user_id*' key).


The use of these commands should result in the following:

As soon as the response from the server contains the '*user_id*' key a new variable (either '*admin_id*' or '*client_id*') is saved to the store.  
The '*admin_id*' variable holds the value of the '*user_id*' key from responses to the curl saved under the '*get_admin*' name.  
The '*client_id*' variable holds the value of the '*user_id*' key from responses to the curl saved under the '*get_client*' name.  

2. **Accept 2nd argument**

The application currently supports arguments for some of the commands.  
For example, the command ```execute``` prompts for the name of the curl from the store on a new line, while the name
can well be provided in the same line as ```execute curl_command_name``` where '*curl_command_name*' is the name of a curl from the store.
In this sample there is no logical continuation of this command, since curls saved to the store are self-sufficient and 
require no arguments.

Though some commands like ```set``` (for setting a specific value to a certain variable) may well adopt the use of the 3rd argument.
For the moment, when we use the ```set var_name``` command, the app requests to enter the value for the variable '*var_name*'
on a new line.  
If we execute something like ```set var_name1 var_name2``` the app would treat the 3rd entry as another variable name that is to be set
and will prompt for the values for each of the 2 variables in a chain, one after another. The same behaviour is retained for the 4th, 5th and 
further entries.

While this syntax works fine, the practical use of the application proved it to be handy to permit entering both, the name of the variable and its 
value in one line. In order to distinguish weather the 3rd entry is a variable name or a value, we could use the '*to*' keyword. This way the following
syntax: 
```
set var_name to value
```
should set the value '*value*' to the variable named '*var_name*' (or create one if missing).  

Complex entries like ```set var_name1 to value1 var_name2, var_name3 to value3, var_name4``` should be well handled too. Such an input should save
the values for the variables with the '*to*' keyword accordingly, then prompt for the missing values in a chain, each on a new line.