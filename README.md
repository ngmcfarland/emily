# Emily

## Command Line Usage:

```bash
python emily.py
```

## Module Usage:
After cloning the emily project, add your emily directory to the PYTHONPATH environment variable

```bash
export PYTHONPATH="/your/path/to/emily:$PYTHONPATH"
```

You can add the line above to your "~/.profile" or "~/.bash_profile" to persist the change.



Now, from any python module, you can use the following example as a guide for interacting with Emily

```python
import emily

session = emily.Emily()
session.start()

response = session.send('What is your name?')
print(response)
```

You can also pass new brain files to Emily to extend her funcitonality

```python
import emily

session = emily.Emily('/path/to/my/brain_file.json')
session.start()

response = session.send('Do you recognize my custom input?')
print(response)
```