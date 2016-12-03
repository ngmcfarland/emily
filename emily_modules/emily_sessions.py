from conf import emily_sessions_conf as config
import decimal
import random
import json
import sys
import os

source = config.source.upper()
if source == 'DYNAMODB':
    import boto3

curdir = os.path.dirname(__file__)
vars_file = os.path.join(curdir, config.vars_file)
if not os.path.isfile(vars_file):
    with open(vars_file,'w') as f:
        f.write(json.dumps({}))

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_session_count():
    with open(vars_file,'r') as f:
        all_session_vars = json.loads(f.read())
    return len(all_session_vars)


def get_session_vars(session_id):
    if source == 'LOCAL':
        with open(vars_file,'r') as f:
            all_session_vars = json.loads(f.read())
        try:
            session_vars = all_session_vars[str(session_id)]
        except KeyError as e:
            session_vars = {}
        finally:
            return session_vars
    elif source == 'DYNAMODB':
        dynamodb = boto3.resource("dynamodb", region_name=config.region)
        table = dynamodb.Table(config.dynamo_table)
        try:
            response = table.get_item(Key={'session_id': session_id})
        except ClientError as e:
            print(e.response['Error']['Message'])
            session_vars = {}
        else:
            if 'Item' in response:
                session_vars = json.loads(response['Item']['session_vars'])
            else:
                session_vars = {}
        finally:
            return session_vars
    else:
        print("ERROR: Unrecognized source: {}".format(config.source))
        return {}


def set_session_vars(session_id,session_vars):
    if source == 'LOCAL':
        with open(vars_file,'r') as f:
            all_session_vars = json.loads(f.read())
        all_session_vars[str(session_id)] = session_vars
        with open(vars_file,'w') as f:
            f.write(json.dumps(all_session_vars))
    elif source == 'DYNAMODB':
        # Check if session_id already exists
        old_session_vars = get_session_vars(session_id)
        dynamodb = boto3.resource("dynamodb", region_name=config.region)
        table = dynamodb.Table(config.dynamo_table)
        if len(old_session_vars) > 0:
            # perform an update
            try:
                response = table.update_item(
                    Key={'session_id': session_id},
                    UpdateExpression="set session_vars = :vars",
                    ExpressionAttributeValues={
                        ':vars': json.dumps(session_vars)
                    },
                    ReturnValues="UPDATED_NEW"
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
        else:
            # perform an insert
            try:
                response = table.put_item(Item={'session_id': session_id, 'session_vars': json.dumps(session_vars)})
            except ClientError as e:
                print(e.response['Error']['Message'])
    else:
        print("ERROR: Unrecognized source: {}".format(config.source))


def create_new_session(default_session_vars=None):
    # Identify used session ids
    if source == 'LOCAL':
        with open(vars_file,'r') as f:
            all_session_vars = json.loads(f.read())
        used_session_ids = all_session_vars.keys()
        session_id = get_random_session_id()
        while session_id in used_session_ids:
            # If generated session id already in use, get another
            session_id = get_random_session_id()
        # Set default session vars using new id
        if default_session_vars:
            set_session_vars(session_id=session_id,session_vars=default_session_vars)
        else:
            set_session_vars(session_id=session_id,session_vars=config.default_session_vars)
        return session_id
    elif source == 'DYNAMODB':
        dynamodb = boto3.resource("dynamodb", region_name=config.region)
        table = dynamodb.Table(config.dynamo_table)
        try:
            response = table.scan(ProjectionExpression='session_id')
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Items' in response:
                # Get all used session ids as an array from response
                used_session_ids = [x['session_id'] for x in json.loads(json.dumps(response['Items'],cls=DecimalEncoder))]
            else:
                used_session_ids = []
            session_id = get_random_session_id()
            while session_id in used_session_ids:
                # If generated session id already in use, get another
                session_id = get_random_session_id()
            # Set default session vars using new id
            set_session_vars(session_id=session_id,session_vars=config.default_session_vars)
            return session_id
    else:
        print("ERROR: Unrecognized source: {}".format(config.source))
        return None


def get_random_session_id():
    return random.randint(config.min_id,config.max_id)


def remove_session(session_id):
    if source == 'LOCAL':
        with open(vars_file,'r') as f:
            all_session_vars = json.loads(f.read())
        all_session_vars.pop(str(session_id))
        with open(vars_file,'w') as f:
            f.write(json.dumps(all_session_vars))
    elif source == 'DYNAMODB':
        dynamodb = boto3.resource("dynamodb", region_name=config.region)
        table = dynamodb.Table(config.dynamo_table)
        try:
            response = table.delete_item(Key={'session_id':session_id})
        except ClientError as e:
            print(e.response['Error']['Message'])
    else:
        print("ERROR: Unrecognized source: {}".format(config.source))