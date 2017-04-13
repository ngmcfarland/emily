import emily
import sys
import os

# --------------- Configuration Options for Emily ------------------------------

session_vars_table = '<your_dynamodb_table_here>'
dynamo_region = 'us-east-1'


def lambda_handler(event,context):
    if 'session_id' in event.keys():
        response,session_id = emily.stateless(message=event['message'],
            session_id=event['session_id'],
            write_to_log_file=False,
            session_vars_source='DYNAMODB',
            session_vars_path=session_vars_table,
            region=dynamo_region)
    else:
        response,session_id = emily.stateless(message=event['message'],
            write_to_log_file=False,
            session_vars_source='DYNAMODB',
            session_vars_path=session_vars_table,
            region=dynamo_region)
    return response,session_id