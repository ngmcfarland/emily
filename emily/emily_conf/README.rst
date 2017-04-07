===========================
Emily Configuration Options
===========================

log_file
--------

Relative path to desired logging file.

**Default:** log/emily.log

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

write_log_to_file
-----------------

In some cases (like running Emily inside an AWS Lambda), you do not have access to write logs to the local filesystem. If write_log_to_file is False, Emily will still execute Python logging commands, but not write anything to the filesystem, and will ignore the "log_file" parameter.

**Default:** True

emily_port
----------

Port that threaded Emily process listens on. Note that this is separate from the port that the Flask app will lisetn on.

**Default:** 8000

default_session_vars
--------------------

Default session variables that every user gets when requesting a session.

**Default:** {'conversation':'default'}

brain_source
------------

Instructs Emily on where to retrieve brain files.

**Default:** LOCAL

**Options:**

- LOCAL - local file system
- DYNAMODB - DynamoDB table in AWS

brain_path
----------

Path to brain directory locally if brain_source: LOCAL.
DynamoDB table name if brain_source: DYNAMODB.

**Default:** brain

session_vars_source
-------------------

Instructs Emily on where to store session variables.

**Default:** LOCAL

**Options:**

- LOCAL - local file system
- DYNAMODB - DynamoDB table in AWS

session_vars_path
-----------------

Path to session variable file locally if session_vars_source: LOCAL.
DynamoDB table name if session_vars_source: DYNAMODB.

**Default:** data/session_vars.json

region
------

When source is DYNAMODB, used to specify AWS region. Not used when source is LOCAL.

**Default:** us-east-1

intent_command
--------------

Optional python command that can be used to determine which brain file to match input against.

**Default:** null

**Example:** go_find_intent.example("{user_input}")

Emily will expect a string value in return that represents the matching intent, and use that to match against the "intent" of known brain files.

preformat_command
-----------------

Depending on your project, you may prefer to have custom code pre-format the user's input before matching to patterns in brain files. This parameter allows a custom python function to be specified.

**Default:** null

**Example:** preformat_the_input.example("{user_input}")

Emily will expect a string value in return that will be used as the new value for "user_input".

starting_node
-------------

This parameter is useful for bots with a very narrow focus. It is used in conjunction with Conversations and specifies which node the user should start on after obtaining a session.

**Default:** null