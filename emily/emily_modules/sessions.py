import decimal
import random
import json
import os

curdir = os.path.dirname(os.path.realpath(__file__))


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def init_config(session_vars_path):
    file_path = os.path.join(curdir,session_vars_path)
    if not os.path.isfile(file_path):
        with open(file_path,'w') as f:
            f.write(json.dumps({}))


def get_session_count(session_vars_path):
    with open(os.path.join(curdir,session_vars_path),'r') as f:
        all_session_vars = json.loads(f.read())
    return len(all_session_vars)


def get_session_vars(session_id,source,session_vars_path,region='us-east-1'):
    if source.upper() == 'LOCAL':
        init_config(session_vars_path=session_vars_path)
        with open(os.path.join(curdir,session_vars_path),'r') as f:
            all_session_vars = json.loads(f.read())
        try:
            session_vars = all_session_vars[str(session_id)]
        except KeyError as e:
            session_vars = {}
        finally:
            return session_vars
    elif source.upper() == 'DYNAMODB':
        import boto3
        from botocore.exceptions import ClientError
        dynamodb = boto3.resource("dynamodb", region_name=region.lower())
        table = dynamodb.Table(session_vars_path)
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
        print("ERROR: Unrecognized source: {}".format(source))
        return {}


def set_session_vars(session_id,session_vars,source,session_vars_path,region='us-east-1'):
    if source.upper() == 'LOCAL':
        init_config(session_vars_path=session_vars_path)
        with open(os.path.join(curdir,session_vars_path),'r') as f:
            all_session_vars = json.loads(f.read())
        all_session_vars[str(session_id)] = session_vars
        with open(os.path.join(curdir,session_vars_path),'w') as f:
            f.write(json.dumps(all_session_vars))
    elif source.upper() == 'DYNAMODB':
        import boto3
        from botocore.exceptions import ClientError
        # Check if session_id already exists
        old_session_vars = get_session_vars(session_id=session_id,source=source,session_vars_path=session_vars_path,region=region)
        dynamodb = boto3.resource("dynamodb", region_name=region.lower())
        table = dynamodb.Table(session_vars_path)
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
        print("ERROR: Unrecognized source: {}".format(source))


def create_new_session(default_session_vars,source,session_vars_path,region='us-east-1'):
    if 'default_session_vars' not in default_session_vars:
        default_session_vars['default_session_vars'] = dict(default_session_vars)
    # Identify used session ids
    if source.upper() == 'LOCAL':
        init_config(session_vars_path=session_vars_path)
        with open(os.path.join(curdir,session_vars_path),'r') as f:
            all_session_vars = json.loads(f.read())
        used_session_ids = all_session_vars.keys()
        session_id = get_random_session_id()
        while session_id in used_session_ids:
            # If generated session id already in use, get another
            session_id = get_random_session_id()
        # Set default session vars using new id
        set_session_vars(session_id=session_id,session_vars=default_session_vars,source=source,session_vars_path=session_vars_path,region=region)
        return session_id
    elif source.upper() == 'DYNAMODB':
        import boto3
        from botocore.exceptions import ClientError
        dynamodb = boto3.resource("dynamodb", region_name=region.lower())
        table = dynamodb.Table(session_vars_path)
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
            set_session_vars(session_id=session_id,session_vars=default_session_vars,source=source,session_vars_path=session_vars_path,region=region)
            return session_id
    else:
        print("ERROR: Unrecognized source: {}".format(source))
        return None


def get_random_session_id(min_id=10000,max_id=99999):
    return random.randint(min_id,max_id)


def remove_session(session_id,source,session_vars_path,region='us-east-1'):
    if source.upper() == 'LOCAL':
        init_config(session_vars_path=session_vars_path)
        with open(os.path.join(curdir,session_vars_path),'r') as f:
            all_session_vars = json.loads(f.read())
        all_session_vars.pop(str(session_id))
        with open(os.path.join(curdir,session_vars_path),'w') as f:
            f.write(json.dumps(all_session_vars))
    elif source.upper() == 'DYNAMODB':
        import boto3
        from botocore.exceptions import ClientError
        dynamodb = boto3.resource("dynamodb", region_name=region.lower())
        table = dynamodb.Table(session_vars_path)
        try:
            response = table.delete_item(Key={'session_id':session_id})
        except ClientError as e:
            print(e.response['Error']['Message'])
    else:
        print("ERROR: Unrecognized source: {}".format(source))