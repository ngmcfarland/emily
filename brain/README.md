# Brain Files

Emily's brain files are JSON files that help drive her ability to answer questions and perform actions.

## Structure

Example brain file structure:

```json
{
    "subject": "EXAMPLE",
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
                        ]
                        "response": "I matched it! I also set my_temp_var to: {{my_temp_var}}"
                    }
                }
            ] 
        }
    ]
}
```

## Subjects

Subjects are currently just metadata for where responses are defined.

## Topics

Topics allow Emily to understand things in context, and provide structure for back-and-forth conversations. At all times, there is a session variable with the name "topic". Most of the time, topic is set to "NONE", so any responses from brain files containing "NONE" topics will be matched.

A category in a brain file can temporarily set the "topic" variable to a different topic to have Emily search for matching patterns in that topic first. If a pattern is not matched in the specific topic set by a category, Emily will always check for matches in the "NONE" topic before answering with a default response.

See the personality brain file for examples of topic usage.

## Categories

Categories always contain a "pattern" and a "template". Emily will try to match the user's input to a pattern, and then use the template to determine how to respond.

## Patterns

Patterns should always be upper case, and contain no punctuation.

Emily does support the use of stars ("\*") in patterns. Meaning, a pattern of "HELLO \*" will match a user's input of "Hello, World!". Note that all punctuation (including apostrophes) are stripped from the user's input when matching patterns.

## Templates

Templates direct Emily on how to respond when a pattern is matched. Emily understands the following types:

| Type | Description                             | Supporting Attributes              | Examples                                 |
|------|-----------------------------------------|------------------------------------|------------------------------------------|
| V    | Direct response                         | "response"                         | basic_chat.json - "HELLO"                |
| U    | Redirect to different pattern           | "redirect"                         | basic_chat.json - "GOOD MORNING"         |
| W    | Run command                             | "presponse", "command", "response" | time_and_date.json - "CURRENT TIME"      |
| E    | Choose random template from array       | "responses"                        | personality.json - "TELL ME A JOKE"      |
| WU   | Run command, then redirect to pattern   | "presponse", "command", "redirect" | weather.json - "WHAT IS THE TEMPERATURE" |
| Y    | Choose response based on variable value | "var", "conditions", "fallback"    | basic_chat.json - "WHAT IS MY NAME"      |

| Attribute  | Object Type | Description                                                                                                              |
|------------|-------------|--------------------------------------------------------------------------------------------------------------------------|
| response   | string      | Verbatim string for how Emily should respond. Can include references to session variables and command outputs.           |
| redirect   | string      | Pattern that Emily should redirect to for a response.                                                                    |
| presponse  | string      | Short for "Pre-Response". For commands that may take time, a pre-response can be added to acknowledge user input.        |
| command    | string      | Python command. Use module syntax: "datetime.datetime.now()"                                                             |
| responses  | array       | An array of response templates. The templates can be of any of the types listed in the table above.                      |
| var        | string      | The name of the variable that will be checked during the condition template.                                             |
| conditions | array       | An array of categories that Emily will use to match against the value of the "var".                                      |
| fallback   | template    | A response template used as the default during a condition in the event that none of the other conditions are satisfied. |

## Variables

All response template types can use variables in redirects, responses, presponses, conditions, etc. Session variables persist while Emily is running.
Inside of any response template type, you can include an optional parameter for setting variables like this:

```json
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
```

By convention, variable names should be lowercase with underscore-separated words.

Variables can be removed or reset to their defaults (like in the case of the "topic" variable) by including this parameter in any response template:

```json
"reset": ["my_var","topic"]
```

Variables can be referenced by name using the following syntax:

```json
"response": "My variable value is: {{my_var}}"
```

When stars ("\*") are used in the "pattern" value of the category, their matched values can be referenced using the following syntax:

```json
"pattern": "ROSES ARE * VIOLETS ARE *",
"template": {
    "type": "V",
    "response": "You said {{1}} is the color of roses, and {{2}} is the color of violets."
}
```

When running commands inside of response templates (like in the "W" and "WU" types), you can reference the results of the command with the following syntax:

```json
"type": "W",
"command": "my_module.run_something('{{1}}','OTHER')",
"response": "Here are the results: {{}}"
```