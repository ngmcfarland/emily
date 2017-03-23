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
    "conversations": {
      "default": {
        "first_example_node": {
          "node_type": "response",
          "pattern": "match this text",
          "utterances": [
            "or match this text",
            "or match * text"
          ],
          "vars": [
            {
              "name": "my_temp_var",
              "value": "I set this"
            }
          ],
          "responses": [
            "I matched it! I also set my_temp_var to: {my_temp_var}"
          ]
        },
        "second_example_node": {
          "node_type": "router",
          "pattern": "go to other conversation",
          "next_node": "other_conversation.third_example_node"
        }
      },
      "other_conversation": {
        "third_example_node": {
          "node_type": "response",
          "responses": [
            "Say this",
            "or this"
          ],
          "next_node": "fourth_example_node"
        },
        "fourth_example_node": {
          "node_type": "response",
          "responses": [
            "Also say this"
          ]
        }
      }
    }
  }

Example YAML brain file structure:

.. code-block:: yaml

  intent: example
  conversations:
    default:
      first_example_node:
        node_type: response
        pattern: match this text
        utterances:
          - or match this text
          - "or match * text"
        vars:
          -
            name: my_temp_var
            value: I set this
        responses:
          - I matched it! I also set my_temp_var to: {my_temp_var}
      second_example_node:
        node_type: router
        pattern: go to other conversation
        next_node: other_conversation.third_example_node
    other_conversation:
      third_example_node:
        node_type: response
        responses:
          - Say this
          - or this
        next_node: fourth_example_node
      fourth_example_node:
        node_type: response
        responses:
          - Also say this

Intents
-------

By convention, intents are the lowercase, separated by underscores, and equivalent to the brain file name.
If "intent_command" is specified in Emily's settings, Emily will attempt to match the result string from the intent command to the intent of one of her brain files.

Internally, all the conversation nodes are referenced using the following format: <intent>.<conversation>.<node_tag>

In the examples above, the first example node is actually referenced using "example.default.first_example_node", and the third example node is "example.other_conversation.third_example_node".
If <intent> and/or <conversation> are not explicitly stated, local references will be assumed (see "next_node" attribute of "third_example_node").

Conversations
-------------

Conversations are logical groupings of conversation nodes so that Emily can have a coherent conversation without getting confused.
All brain files should include a 'default' conversation, but have the option of including many more conversations.
By setting the "conversation" session variable (see variables section below), you can control which patterns/utterances Emily will match user input against.
By default, the "conversation" session variable is set to 'default' which causes Emily to search for patterns/utterances in 'default' conversations across all her brain files.

In the sample below, you can see that routing the conversation to either "blue_flower" or "red_flower" will change Emily's answer when the user asks "What color is the flower?".

After processing a node inside a non-default conversation, the "conversation" session variable will automatically be reset to 'default'.

If a pattern/utterance from a non-default conversation is not matched to the user input, Emily will also search the default conversations as a fall back.

.. code-block:: json

  {
    "intent": "conversation_example",
    "conversations": {
      "default": {
        "pick_blue_flower": {
          "node_type": "response",
          "pattern": "pick a blue flower",
          "utterances": [
            "choose a blue flower"
          ],
          "responses": [
            "Okay, I have picked the flower."
          ],
          "conversation": "blue_flower"
        },
        "pick_red_flower": {
          "node_type": "response",
          "pattern": "pick a red flower",
          "utterances": [
            "choose a red flower"
          ],
          "responses": [
            "Okay, I have picked the flower."
          ],
          "conversation": "red_flower"
        }
      },
      "blue_flower": {
        "what_color": {
          "node_type": "response",
          "pattern": "what color is it",
          "utterances": [
            "what color is the flower"
          ],
          "responses": [
            "The flower is blue."
          ]
        }
      },
      "red_flower": {
        "what_color": {
          "node_type": "response",
          "pattern": "what color is it",
          "utterances": [
            "what color is the flower"
          ],
          "responses": [
            "The flower is red."
          ]
        }
      }
    }
  }

Nodes
~~~~~

Each conversation is a JSON or YAML object containing conversation nodes. Each node has a unique key by which it is referenced.

The values chosen for node keys are irrelevant save for the fact that they must be unique *within that conversation*. Randomly generated keys can be used, but it is recommended that logical key values be used for human readability.

Node Types
~~~~~~~~~~

There are five node types that can be used in creating a conversation.

=============== ==========================================================================
 Type            Required Attributes
=============== ==========================================================================
 response        "responses"
 router          "next_node" or "node_options"
 simple_logic    "command"
 yes_no_logic    "yes_node", "yes_prime_node", "no_node", "no_prime_node", "unknown_node"
 string_logic    "command", "unknown_node"
=============== ==========================================================================

Optional Attributes for All Types:

============= ===========================================================================================
 Attribute     Description
============= ===========================================================================================
 pattern       A string of text for Emily to match the user's input against
 utterances    Additional strings that Emily will reference when trying to match user input
 error_node    Used with logic nodes, this attribute defines a node to route to in the event of an error
 next_node     The next node to route to after processing the current node
 vars          A list of variables to assign to the user's session variables
 reset         A list of variables to reset after the node has been processed
 preset        A list of variables to reset before the node has been processed
============= ===========================================================================================

**Response:**

Provides Emily with one or more responses to choose from. Response nodes can be chained together to create joined output (example further down).
Once a response node is reached that does not have another response node in the "next_node" attribute, Emily will pause to allow the user to respond.

.. code-block:: json

  "example_greeting_1": {
    "node_type": "response",
    "pattern": "hello",
    "utterances": [
      "hi",
      "hey"
    ],
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
    "next_node": "some_logic_node"
  }

Responses are chosen by Emily at random, but output from above could be:

.. code-block:: bash

    User  >   hi

    Emily >   Hey! How are you today?

    User  >   

**Router:**

A router node is used to match the user's input using patterns and utterances, and route Emily to the appropriate response or logic node.
This is often used to route to a conversation outside of 'default'.
A router node can direct to the next node by using either a 'next_node' attribute (single node) or a 'node_options' attribute (one or more nodes chosen at random).

.. code-block:: json

  {
    "intent": "router_examples",
    "conversations": {
      "default": {
        "catch_input_1": {
          "node_type": "router",
          "pattern": "tell me about cats",
          "utterances": [
            "i want to know about cats",
            "talk about cats"
          ],
          "next_node": "cats.cat_fact"
        },
        "catch_input_2": {
          "node_type": "router",
          "pattern": "tell me about pets",
          "utterances": [
            "i want to know about pets",
            "talk about pets"
          ],
          "node_options": [
            "cats.cat_fact",
            "dogs.dog_fact"
          ]
        }
      },
      "cats": {
        "cat_fact": {
          "node_type": "response",
          "responses": [
            "A group of cats is called a 'clowder'",
            "Cats sleep 70% of their lives",
            "Cats have over 20 muscles that control their ears"
          ]
        }
      },
      "dogs": {
        "dog_fact": {
          "node_type": "response",
          "responses": [
            "Corgi is Welsh for 'dwarf dog'",
            "A dog's sense of smell is 10,000 times stronger than a human's",
            "Dogs have at least 18 muscles in each ear"
          ]
        }
      }
    }
  }

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
    "pattern": "ask me about dogs",
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

Patterns and Utterances
~~~~~~~~~~~~~~~~~~~~~~~

By convention, patterns/utterances are lowercase and do not include any punctuation.

Emily does support the use of stars ("\*") in patterns. Meaning, a pattern of "HELLO \*" will match a user's input of "Hello, World!". Note that all punctuation (including apostrophes) are stripped from the user's input when matching patterns.

Utterances follow the same conventions as patterns. The list of utterances is simply a convenience so that a single template can be accessed by multiple patterns.

Note: YAML syntax requires that patterns or utterances that contain a "*" be enclosed in double quotes. See YAML example above.

Variables
~~~~~~~~~

All node types can use variables in patterns, utterances, responses, and commands. Session variables persist while Emily is running.
Inside of any node, you can include an optional parameter for setting variables like this:

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

Variables can be removed or reset to their defaults (like in the case of the "conversation" variable) by including this parameter in any response template:

.. code-block:: json

  "reset": ["my_var","conversation"]

**Note:** The variables specified in the "reset" attribute will be reset *after* the template has been processed.
Meaning the variables are still available for commands, responses, redirects, etc.
At times, this is not the desired behavior, so there is a second option that resets the variable values *before* any further processing of the template:

.. code-block:: json

  "preset": ["my_var","conversation"]

Variables can be referenced by name using the following syntax:

.. code-block:: json

  "response": "My variable value is: {my_var}"

When stars ("\*") are used in the "pattern" value of the category, their matched values can be referenced using the following syntax:

.. code-block:: json

  "node_type": "response",
  "pattern": "roses are * violets are *",
  "responses": [
    "You said {1} is the color of roses, and {2} is the color of violets."
  ]

When running commands inside of logic nodes (like the "simple_logic", "yes_no_logic", and "string_logic" types), you can reference the results of the command with the following syntax:

.. code-block:: json

  "logic_example": {
    "node_type": "simple_logic",
    "pattern": "process *",
    "command": "my_module.run_something('{1}','OTHER')",
    "next_node": "response_example"
  },
  "response_example": {
    "node_type": "response",
    "responses": [
      "Okay, I processed {command_result}"
    ]
  }

The above syntax ("{command_result}") will return the entire result in the response, regardless of whether the response is a string or other type of Python object.
A more helpful method is to have your custom function defined in the "command" attribute return a Python dictionary.
When a dictionary is returned, Emily automatically adds all of the dictionary's key-value pairs to the current session variables which makes them usable in responses, redirects, etc.


.. code-block:: python

    # Example function inside my_module.py
    def split_by_spaces(input_string):
        string1,string2 = input_string.split(" ")
        return {'first':string1,'second':string2}

.. code-block:: json

  "logic_example": {
    "node_type": "simple_logic",
    "pattern": "split *",
    "command": "my_module.split_by_spaces(input_string='{1}')",
    "next_node": "response_example"
  },
  "response_example": {
    "node_type": "response",
    "vars": [
      {
        "name": "saved_for_later",
        "value": "{first}, {second}"
      }
    ],
    "responses": [
      "First string: {first}, Second string: {second}"
    ]
  }

**Note that Emily will overwrite any previous session variables with the values returned in the command's response**
