# Emily

## Command Line Usage:

python emily.py


## Module Usage:
After cloning the emily project, add your emily directory to the PYTHONPATH environment variable

export PYTHONPATH="/your/path/to/emily:$PYTHONPATH"

You can add the line above to your "~/.profile" or "~/.bash_profile" to persist the change.



Now, from any python module, you can use the following example as a guide for interacting with Emily


import emily


session = emily.Emily()

session.start()


response = session.send('Hello')