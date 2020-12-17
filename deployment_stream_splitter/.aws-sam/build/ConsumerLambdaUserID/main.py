from fastapi import FastAPI
import boto3
import time
import json
import pandas as pd
from mangum import Mangum

ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
SECRET_KEY = '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'

client = boto3.client(
    'kinesis',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

def predict(df):
    return 0.95

app = FastAPI(root_path = "/prod")


@app.get("/")
async def root():
    return {"message": "stream splitter"}

@app.get("/split_stream/userid/{userid}")
async def get_stream_by_userid(userid: int):
    shard_id = 'shardId-000000000000' #we only have one shard!
    shard_it = client.get_shard_iterator(StreamName="telemetry-power-consumption", ShardId=shard_id, \
        ShardIteratorType="LATEST")["ShardIterator"]
    t_end = time.time() + 120
    while time.time()<t_end:
        out = client.get_records(ShardIterator=shard_it, Limit=2)
        group_records = []
        df = pd.DataFrame()
        for record in out['Records']:
            if record['PartitionKey'] == str(userid):
                sample = json.loads(record['Data'])
                df_to_append = pd.json_normalize(sample)
                df = df.append(df_to_append)
            prediction = predict(df)
            content_dict = {'user_id': userid, 'prediction': prediction}
            content_dict = json.dumps(content_dict).encode('utf-8')
            client.put_record(StreamName="power-usage-prediction", Data=content_dict, \
            PartitionKey="partitionkey")
        shard_it = out["NextShardIterator"]
        print(out)
        print('\n')
        time.sleep(5)
    
    return {'message': 'success'}

handler = Mangum(app)
