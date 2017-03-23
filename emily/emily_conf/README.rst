===========================
Emily Configuration Options
===========================

log_file
--------

Relative path to desired logging file.

**Default:** log/emily.log

brain_dir
---------

Relative path to directory containing brain files.

**Default:** brain

logging_level
-------------

Desired logging level.

**Default:** DEBUG

**Options:**

- CRITICAL
- ERROR
- WARNING
- INFO
- DEBUG

emily_port
----------

Port that threaded Emily process listens on.

**Default:** 8000

default_session_vars
--------------------

Default session variables that every user gets when requesting a session.

**Default:** {'topic':'NONE'}

source
------

Instructs Emily on where to store session variables and other data.

**Default:** LOCAL

**Options:**

- LOCAL - local file system
- DYNAMODB - DynamoDB tables in AWS

session_vars_path
-----------------

Path to session variable file locally if source: LOCAL.
DynamoDB table name if source: DYNAMODB.

**Default:** conf/session_vars.json

**Note:** When using local file path, path is relative to the sessions.py module in emily_modules directory.

region
------

When source is DYNAMODB, used to specify AWS region. Not used when source is LOCAL.

**Default:** us-east-1

intent_command
--------------

Optional python command that can be used to determine which brain file to match input against.

**Default:** null

**Example:** go_find_intent.example("user_input")

Emily will expect a string value in return that represents the matching intent, and use that to match against the "intent" of known brain files.

preformat_command
-----------------

Depending on your project, you may prefer to have custom code pre-format the user's input before matching to patterns in brain files. This parameter allows a custom python function to be specified.

**Default:** null

**Example:** preformat_the_input.example("user_input")

Emily will expect a string value in return that will be used as the new value for "user_input".

starting_node
-------------

This parameter is useful for bots with a very narrow focus. It is used in conjunction with Conversations and specifies which node the user should start on after obtaining a session.

**Default:** null