===========
Brain Files
===========

Emily's brain files are configuration files that help drive her ability to answer questions and perform actions.
Emily can parse and understand both JSON and YAML brain files. The YAML syntax is easier for a human to read and write, and the JSON syntax is easier generate using code.
Both syntaxes have the same parameters, and can access the same features. Sample code in this document will use the JSON syntax.

Structure
---------

Example JSON brain file structure:

.. code-block:: json

  {
    "intent": "example",
    "topics": [
      {
        "topic": "NONE",
        "categories": [
          {
            "pattern": "MATCH THIS TEXT",
            "template": {
              "type": "V",
              "vars": [
                {
                  "name": "my_temp_var",
                  "value": "I set this"
                }
              ],
              "response": "I matched it! I also set my_temp_var to: {{my_temp_var}}"
            },
            "utterances": [
              "OR MATCH THIS TEXT",
              "OR MATCH * TEXT"
            ]
          }
        ] 
      }
    ],
    "conversations": {
      "example_node": {
        "node_type": "response",
        "responses": [
          "Say this",
          "Or this"
        ],
        "next_node": "example_node_2"
      },
      "example_node_2": {
        "node_type": "response",
        "responses": [
          "Also say this"
        ]
      }
    }
  }

Example YAML brain file structure:

.. code-block:: yaml

  intent: example
  topics:
    -
      topic: NONE
      categories:
        -
          pattern: MATCH THIS TEXT
          template:
            type: V
            vars:
              -
                name: my_temp_var
                value: I set this
            response: I matched it! I also set my_temp_var to: {{my_temp_var}}
          utterances:
            - OR MATCH THIS TEXT
            - "OR MATCH * TEXT"
  conversations:
    example_node:
      node_type: response
      responses:
        - Say this
        - Or this
      next_node: example_node_2
    example_node_2: {
      node_type: response
      responses:
        - Also say this

Intents
-------

By convention, intents are the uppercase equivalent of the brain file name. If "intent_command" is specified in Emily's settings, Emily will attempt to match the result string from the intent command to the intent of one of her brain files.

Topics
------

Topics allow Emily to understand things in context, and provide structure for *extremely simple* back-and-forth conversations (for more complicated converations, use conversation nodes shown below). At all times, there is a session variable with the name "topic". Most of the time, topic is set to "NONE", so any responses from brain files containing "NONE" topics will be matched.

A category in a brain file can temporarily set the "topic" variable to a different topic to have Emily search for matching patterns in that topic first. If a pattern is not matched in the specific topic set by a category, Emily will always check for matches in the "NONE" topic before answering with a default response.

See the personality brain file for examples of topic usage.

Categories
~~~~~~~~~~

Categories always contain a "pattern" and a "template", and can optionally contain "utterances" (other patterns that should have the same result). Emily will try to match the user's input to a pattern or utterance, and then use the template to determine how to respond.

Patterns and Utterances
~~~~~~~~~~~~~~~~~~~~~~~

*Patterns should always be upper case, and contain no punctuation.*

Emily does support the use of stars ("\*") in patterns. Meaning, a pattern of "HELLO \*" will match a user's input of "Hello, World!". Note that all punctuation (including apostrophes) are stripped from the user's input when matching patterns.

Utterances follow the same conventions as patterns. The list of utterances is simply a convenience so that a single template can be accessed by multiple patterns.

Note: YAML syntax requires that patterns or utterances that contain a "*" be enclosed in double quotes. See YAML example above.

Templates
~~~~~~~~~

Templates direct Emily on how to respond when a pattern or utterance is matched. Emily understands the following types:

======= ========================================= ==================================== ============================================================================
 Type    Description                               Supporting Attributes                Examples
======= ========================================= ==================================== ============================================================================
 V       Direct response                           "response"                           basic_chat.json - "HELLO"
 U       Redirect to different pattern             "redirect"                           Primarily used for re-formatting user input
 W       Run command                               "presponse", "command", "response"   time_and_date.json - "CURRENT TIME"
 E       Choose random template from array         "responses"                          jokes.yaml - "TELL ME A JOKE"
 WU      Run command, then redirect to pattern     "presponse", "command", "redirect"   While supported, this functionality better achieved through conversations.
 Y       Choose response based on variable value   "var", "conditions", "fallback"      basic_chat.json - "WHAT IS MY NAME"
 C       Start a conversation                      "node"                               sports.json - "ASK ME ABOUT SPORTS"
======= ========================================= ==================================== ============================================================================

============ ============= ==========================================================================================================================
 Attribute    Object Type   Description
============ ============= ==========================================================================================================================
 response     string        Verbatim string for how Emily should respond. Can include references to session variables and command outputs.
 redirect     string        Pattern that Emily should redirect to for a response.
 presponse    string        Short for "Pre-Response". For commands that may take time, a pre-response can be added to acknowledge user input.
 command      string        Python command. Use module syntax: "datetime.datetime.now()"
 responses    array         An array of response templates. The templates can be of any of the types listed in the table above.
 var          string        The name of the variable that will be checked during the condition template.
 conditions   array         An array of categories that Emily will use to match against the value of the "var".
 fallback     template      A response template used as the default during a condition in the event that none of the other conditions are satisfied.
 node         string        Unique key for a conversation node. See Conversations for more details.
============ ============= ==========================================================================================================================

In addition to these attributes, there are special attributes used for setting and resetting variables as defined below.

Variables
~~~~~~~~~

All response template types can use variables in redirects, responses, presponses, conditions, etc. Session variables persist while Emily is running.
Inside of any response template type, you can include an optional parameter for setting variables like this:

.. code-block:: json

  "vars": [
    {
      "name": "my_var",
      "value": "This is the value"
    },
    {
      "name": "my_other_var",
      "value": "This is the other value"
    }
  ]

By convention, variable names should be lowercase with underscore-separated words.

Variables can be removed or reset to their defaults (like in the case of the "topic" variable) by including this parameter in any response template:

.. code-block:: json

  "reset": ["my_var","topic"]

**Note:** The variables specified in the "reset" attribute will be reset *after* the template has been processed.
Meaning the variables are still available for commands, responses, redirects, etc.
At times, this is not the desired behavior, so there is a second option that resets the variable values *before* any further processing of the template:

.. code-block:: json

  "preset": ["my_var","topic"]

Variables can be referenced by name using the following syntax:

.. code-block:: json

  "response": "My variable value is: {{my_var}}"

When stars ("\*") are used in the "pattern" value of the category, their matched values can be referenced using the following syntax:

.. code-block:: json

  "pattern": "ROSES ARE * VIOLETS ARE *",
  "template": {
    "type": "V",
    "response": "You said {{1}} is the color of roses, and {{2}} is the color of violets."
  }

When running commands inside of response templates (like in the "W" and "WU" types), you can reference the results of the command with the following syntax:

.. code-block:: json

  "type": "W",
  "command": "my_module.run_something('{{1}}','OTHER')",
  "response": "Here are the results: {{}}"

The above syntax ("{{}}") will return the entire result in the response, regardless of whether the response is a string or other type of Python object.
A more helpful method is to have your custom function defined in the "command" attribute return a Python dictionary.
When a dictionary is returned, Emily automatically adds all of the dictionary's key-value pairs to the current session variables which makes them usable in responses, redirects, etc.


.. code-block:: python

    # Example function inside my_module.py
    def split_by_dash(input_string):
        string1,string2 = input_string.split("-")
        return {'first':string1,'second':string2}

.. code-block:: json

  "type": "W",
  "command": "my_module.split_by_dash(input_string='try-this')",
  "response": "First string: {{first}}, Second string: {{second}}"

**Note that Emily will overwrite any previous session variables with the values returned in the command's response**

Conversations
-------------

Topics, patterns, and templates are useful for intelligently responding to a wide variety of user inputs, but they become very complex in interactions that involve more than a call and response.
Conversations create a simple way of defining a flow of questions and responses which can mimic natural speech. They allow Emily to easily go deeper on one subject without losing context or getting confused.

  *When writing a brain file, use topics to go wide, and conversations to go deep.*

For an example of conversations, look at the "sports.json" brain file and the "sports.py" module in emily/emily_modules.

Nodes
~~~~~

The "conversations" attribute in the brain file is a JSON or YAML object containing conversation nodes. Each node has a unique key by which it is referenced.

The values chosen for node keys are irrelevant save for the fact that they must be unique *within that brain file*. Randomly generated keys can be used, but it is recommended that logical key values be used for human readability.

Node Types
~~~~~~~~~~

There are five node types that can be used in creating a conversation.

=============== ==========================================================================
 Type            Required Attributes
=============== ==========================================================================
 response        "responses"
 string_logic    "command", "unknown_node"
 yes_no_logic    "yes_node", "yes_prime_node", "no_node", "no_prime_node", "unknown_node"
 simple_logic    "command"
 error           "responses"
=============== ==========================================================================

Optional Attributes for All Types:

"error_node", "next_node"

**Response:**

Provides Emily with one or more responses to choose from. Response nodes can be chained together to create joined output (example further down).
Once a response node is reached that does not have another response node in the "next_node" attribute, Emily will pause to allow the user to respond.

.. code-block:: json

  "example_greeting_1": {
    "node_type": "response",
    "responses": [
      "Hello!",
      "Hey!",
      "Howdy!"
    ],
    "next_node": "example_greeting_2"
  },
  "example_greeting_2": {
    "node_type": "response",
    "responses": [
      "How are you today?",
      "How's your day going?"
    ],
    "next_node": "some_other_node"
  }

Responses are chosen by Emily at random, but output from above could be:

.. code-block:: bash

    Emily >   Hey! How are you today?

    User  >   

**Simple Logic:**

This node type is used for running Python functions.
The results of the function will be added to session variables (see Variables section above), but the direction of the conversation is not changed by the command.
Useful for logging user input or fetching answers to a question.

.. code-block:: json

  "record_input": {
    "node_type": "simple_logic",
    "command": "some_module.record_this('{user_input}')",
    "error_node": "catch_all_error",
    "next_node": "some_other_node"
  }

**Note:** {user_input} is automatically replaced with the verbatim of what the user entered.

**Yes/No Logic:**

Many of Emily's interactions involve her asking yes-or-no questions to the user.
The yes_no_logic node type determines how the user answered the yes-or-no question, and decides what to do or say next.

Possible Answers:

- Yes - The user used a form of yes ("yep","absolutely","yeah",etc.)
- Yes Prime - The user used a form of yes, but also included more information in response ("Yeah, but I only like big dogs")
- No - The user used a form of no ("nope","negative","nah")
- No Prime - The user used a form of no, but also included more information in response ("No, I only like cats")
- Unknown - Emily could not recognize the user's input as a yes or no answer (they are possibly not answering the question)

.. code-block:: json

  "ask_about_dogs": {
    "node_type": "response",
    "responses": [
      "Do you like dogs?"
    ],
    "next_node": "does_user_like_dogs"
  },
  "does_user_like_dogs": {
    "node_type": "yes_no_logic",
    "yes_node": "i_like_dogs_too",
    "yes_prime_node": "parse_additional_info",
    "no_node": "thats_too_bad",
    "no_prime_node": "parse_additional_info",
    "unknown_node": "get_intent"
  }

**Note:** The nodes following yes_prime and no_prime are often other logic nodes. Emily automatically removes the yes or no phrase from the user input.
For example, if "i_like_dogs_too" uses "{user_input}" in its command, and the original user input was "Yeah, but I only like big dogs", then "but I only like big dogs" is what "{user_input}" will evaluate to.

**String Logic:**

The string_logic node type is similar to the yes_no_logic type, but allows for custom values to be evaluated.

.. code-block:: json

  "ask_favorite_dog": {
    "node_type": "response",
    "responses": [
      "What is your favorite type of dog?"
    ],
    "next_node": "parse_answer"
  },
  "parse_answer": {
    "node_type": "string_logic",
    "command": "dogs.check_dog_type('{user_input}')",
    "error_node": "catch_all_error",
    "lab": "lab_response",
    "great_dane": "great_dane_response",
    "unknown_node": "dont_know_response"
  }

*Functions used with string_logic nodes **must** return a dictionary with a key of 'string'*

The 'string' value will be compared to the attributes in the string_logic node and the "unknown_node" will be used if a match is not found.

In the example above, if the user answered "What is your favorite type of dog?" with "A labrador" and the check_dog_type function returns {'string': 'lab'}, Emily will go to "lab_response".

**Error:**

The error node type is similar to a response node, and allows Emily to gracefully exit a conversation when she gets lost or confused by a user's input.

.. code-block:: json

  "catch_all_error": {
    "node_type": "error",
    "responses": [
      "I'm sorry, I don't know what you're asking",
      "I got a little confused there..."
    ]
  }