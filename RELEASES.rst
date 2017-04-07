Releases
--------

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