import emily

# --------------- Configuration Options for Emily ------------------------------

session_vars_table = '<your_dynamodb_table_here>'
dynamo_region = 'us-east-1'


emily_params = {'session_vars_source':'DYNAMODB',
    'session_vars_path':session_vars_table,
    'region':dynamo_region,
    'log_file':'/opt/python/log/emily.log'}

application = emily.start_emily(**emily_params)

if __name__ == '__main__':
    application.run()