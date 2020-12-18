import boto3
import time
import json
import base64
# from decimal import Decimal
#import ast

def load2table(payload):
    resource = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id='AKIAW6VXUO4OZDG5KBYV', aws_secret_access_key='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')
    table = resource.Table("ConsumerTable")

    item = payload

    table.put_item(Item=item)
    print("record loaded to dynamoDB.")

def lambda_handler(event, context):
    for record in event['Records']:
       #Kinesis data is base64 encoded so decode here
       payload=base64.b64decode(record["kinesis"]["data"])
       print('payload-->', payload)
       print('type-->', type(payload))
       payload = payload.decode('utf-8')
       payload = json.dumps(payload)
       payload = json.loads(payload)
       json_acceptable_string = payload.replace("'", "\"")
       data = json.loads(json_acceptable_string)
       print('data', data)
       for key in data:
            if key != 'Date' and key != 'Time':
                data[key] = str(data[key])
       load2table(data)          



