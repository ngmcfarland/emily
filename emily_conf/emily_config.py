log_file = 'log/emily.log'
brain_dir = 'brain'
logging_level = 'DEBUG'
emily_port = 8000
default_session_vars = {'topic':'NONE'}

"""Optional Parameters for Alternate Functionality"""

# By setting intent_filter to True, and setting intent_command to your own custom function,
# Emily will run the command and pass the user_input to your function. She will expect a string
# value in return, and use that value to filter the brain files by intent.
intent_filter = False
intent_command = 'go_find_intent.example("user_input")'

# By setting preformat_filter to True, and setting preformat_command to your own custom function,
# Emily will run the command and pass the user_input to your function. She will expect a string
# value in return, and use that value as the new user_input to pass to the brain files.
preformat_filter = False
preformat_command = 'preformat_the_input.example("user_input")'