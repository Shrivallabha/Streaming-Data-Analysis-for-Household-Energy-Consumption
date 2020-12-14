from fastapi import FastAPI
import boto3
import pandas as pd
import json
import time

app = FastAPI()

ACCESS_KEY = 'AKIAW6VXUO4OULN7JM4K'
SECRET_KEY = '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'

client = boto3.client(
    'kinesis',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

def records_to_kinesis(RecordKinesis):
        start = time.clock()
        response = client.put_records(Records=RecordKinesis, StreamName='LoadtestKinesis')
        print ("Time taken to process" +  len(Records) + " is " +time.clock() - start)
        return response

@app.get("/")
async def root():
    return {"message": "real-time serverless ML predictions on electricity consumption"}

@app.get("/put_record")
def put_record():
    df = pd.read_csv('test_data_6months')
    for i in range(50):
        content_dict = df.iloc[i].to_json()
        content_dict = json.dumps(json.loads(content_dict))
        client.put_records(StreamName="telemetry-power-consumption", Data=[content_dict], \
            PartitionKey="partitionkey")
        time.sleep(5)    

    
    return 'successful'

@app.get("/put_records")
def put_records():
    
    df = pd.read_csv('test_data_6months')
    Records = []
    count = 0
    for i in range(50):
        value1 = df.iloc[i]['Unnamed: 0'].astype('str')
        if value1 is None:
            value1 = '0'
        # data = json.dumps(json.loads(df.iloc[i].to_json()))    
        record = {'Data': df.iloc[i].to_json(),'PartitionKey':value1 }
        Records.append(record)
        count +=1
        if count == 10:
            response = client.put_records(Records=Records, StreamName='telemetry-power-consumption')
            time.sleep(5)
            Records = []
            count = 0   
    
    return 'success'             