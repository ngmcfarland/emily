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

You can also pass an array of new brain files to Emily to extend her funcitonality

```python
import emily

session = emily.Emily(more_brains=['/path/to/my/brain_file.json'])
session.start()

response = session.send('Do you recognize my custom input?')
print(response)
```

If you are extending Emily's functionality for a project and would like to not include Emily's default brain files, you can use an additional parameter to run a lighter version of Emily.

```python
import emily

session = emily.Emily(more_brains=['/path/to/my/brain_file.json'],disable_emily_defaults=True)
session.start()

response = session.send('Do you recognize my custom input?')
print(response)
```

## Brain Files

See documentation here: [Brain Files](/brain)

## Configuration Options

See documentation here: [Configuration Options](/emily_conf)