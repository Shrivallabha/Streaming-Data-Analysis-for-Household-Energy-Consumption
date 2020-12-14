import boto3
import pandas as pd
import time
import json


ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
SECRET_KEY = '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'

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY
    )

kinesis_client = boto3.client(
    'kinesis',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

s3_client = boto3.client('s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY)

def lambda_handler(event, context):

    event_list = []
    Records = []
    for record in event['Records']:
        event_list.append(record['s3']['object']['key'])
    if (len(event_list) == 1):
        key = event_list[0]
        user_id = key.split('_')[0]
        my_bucket = s3.Bucket("s3datastreaming")

        for object_summary in my_bucket.objects.filter(Prefix=user_id):
            print('Found file %s' % object_summary.key)
            file = s3_client.download_file("s3datastreaming", str(object_summary.key), '/tmp/streaming_file')
        
        df = pd.read_csv('/tmp/streaming_file')
    
        count = 0
        for i in range(50):
            # value1 = df.iloc[i]['Unnamed: 0'].astype('str')
            # if value1 is None:
            #     value1 = '0'
            # data = json.dumps(json.loads(df.iloc[i].to_json()))
            value1 = user_id    
            record = {'Data': df.iloc[i].to_json(),'PartitionKey':value1 }
            Records.append(record)
            count +=1
            if count == 10:
                response = kinesis_client.put_records(Records=Records, StreamName='telemetry-power-consumption')
                time.sleep(5)
                Records = []
                count = 0

    else:
        print('List size more than one')    
