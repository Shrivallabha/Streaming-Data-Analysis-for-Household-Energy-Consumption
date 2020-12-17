import boto3
import time
import json
import base64
from decimal import Decimal
import ast

def load2table(payload):
    resource = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id='AKIAW6VXUO4OULN7JM4K', aws_secret_access_key='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')
    table = resource.Table("ConsumerTable")

    item = payload

    table.put_item(Item=item)
    print("record loaded to dynamoDB.")

def lambda_handler(event, context):
    for record in event['Records']:
       #Kinesis data is base64 encoded so decode here
       payload=base64.b64decode(record["kinesis"]["data"])
       payload = payload.decode('utf-8')
       payload = ast.literal_eval(payload)
       for key in payload:
           if key != 'Date' and key != 'Time':
                payload[key] = Decimal(payload[key]) 
       load2table(payload)


