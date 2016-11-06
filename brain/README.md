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
                                "name": "MY_TEMP_VAR",
                                "value": "I set this"
                            }
                        ]
                        "response": "I matched it! I also set MY_TEMP_VAR to: {{MY_TEMP_VAR}}"
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

Topics allow Emily to understand things in context, and provide structure for back-and-forth conversations. At all times, there is a session variable with the name "TOPIC". Most of the time, topic is set to "NONE", so any responses from brain files containing "NONE" topics will be matched.

A category in a brain file can temporarily set the "TOPIC" variable to a different topic to have Emily search for matching patterns in that topic first. If a pattern is not matched in the specific topic set by a category, Emily will always check for matches in the "NONE" topic before answering with a default response.

See the personality brain file for examples of topic usage.

## Categories

Categories always contain a "pattern" and a "template". Emily will try to match the user's input to a pattern, and then use the template to determine how to respond.

## Patterns

Patterns should always be upper case, and contain no punctuation.

Emily does support the use of stars ("*") in patterns. Meaning, a pattern of "HELLO *" will match a user's input of "Hello, World!". Note that all punctuation (including apostrophes) are stripped from the user's input when matching patterns.

## Templates

Templates direct Emily on how to respond when a pattern is matched. Emily understands the following types:

| Type | Description                             | Supporting Variables               | Examples                                 |
|------|-----------------------------------------|------------------------------------|------------------------------------------|
| V    | Direct response                         | "response"                         | basic_chat.json - "HELLO"                |
| U    | Redirect to different pattern           | "redirect"                         | basic_chat.json - "GOOD MORNING"         |
| W    | Run command                             | "presponse", "command", "response" | time_and_date.json - "CURRENT TIME"      |
| E    | Choose random template from array       | "responses"                        | personality.json - "TELL ME A JOKE"      |
| WU   | Run command, then redirect to pattern   | "presponse", "command", "redirect" | weather.json - "WHAT IS THE TEMPERATURE" |
| Y    | Choose response based on variable value | "var", "conditions", "fallback"    | basic_chat.json - "WHAT IS MY NAME"      |