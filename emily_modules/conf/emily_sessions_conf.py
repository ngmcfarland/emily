# Use LOCAL for local session variable storage
# Use DYNAMODB for AWS storage
source = 'LOCAL'

# Core variables
default_session_vars = {'topic':'NONE'}
min_id = 10000
max_id = 99999

# Local variables
vars_file = 'conf/session_vars.json'

# DynamoDB variables
region = 'us-east-1'
dynamo_table = 'emily-session-vars'