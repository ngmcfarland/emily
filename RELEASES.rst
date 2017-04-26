Releases
--------

1.0.6 (2017-04-26)
++++++++++++++++++

**Bugfixes**

- Allowed for preferred session IDs in 1.0.5, which means session IDs may be strings or integers, but Emily was still trying to cast session IDs as integers.

1.0.5 (2017-04-26)
++++++++++++++++++

**Improvements**

- Support for preferred session IDs when posting to /get_session or calling the get_session() function in the Emily() class. 
- Introduced templates for hosting Emily in AWS Lambda and Beanstalk, and for having Emily interact with Amazon's Alexa.

**Bugfixes**

- get_session_vars had a bug when using DynamoDB as the source for session variables.

1.0.4 (2017-04-11)
++++++++++++++++++

**Bugfixes**

- Emily's default log file is 'emily/log/emily.log', but the empty log directory was not included in the wheel. Added log directory path to MANIFEST.in
- Escaped single quote in README.rst that caused the syntax highlights in the command line example to look off.

1.0.3 (2017-04-07)
++++++++++++++++++

**Improvements**

- Added function to setup.py for removing links in README.rst when creating the long description. PyPI does not display the description properly when there are links.

**Bugfixes**

- Forgot to make "user_input" change to Emily's stateless function in release 1.0.2

1.0.2 (2017-04-07)
++++++++++++++++++

**Improvements**

- Preformat and intent filters (configured through config file) were expecting "user_input" instead of "{user_input}", which was inconsistent with user_input logic in nodes. Now the user's input is always referenced using "{user_input}" no matter where it is referenced.
- Emily has always set user input to lowercase and removed all puncuation before matching it to patterns. Previously, when "{user_input}" was referenced in commands and responses, this formatted version of the input was used. Changed code so that now "{user_input}" is replaced with the raw input of the user, complete with capitalization and punctuation.

1.0.1 (2017-03-27)
++++++++++++++++++

**Bugfixes**

- Previous version of setup.py tried to import emily and reference version, but did so before installing dependencies, so setup.py always failed while installing from PyPI. Changed location of version to setup.py.


1.0.0 (2017-03-27)
++++++++++++++++++

- Initial attempt at releasing Emily to PyPI
- All features specified in README files should be available