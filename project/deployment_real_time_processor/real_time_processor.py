from fastapi import FastAPI
import boto3
import time
import json

app = FastAPI()

ACCESS_KEY = 'AKIAW6VXUO4OULN7JM4K'
SECRET_KEY = '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'

client = boto3.client(
    'kinesis',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

@app.get("/")
async def root():
    return {"message": "real time processor"}

@app.get("/real_time_inference/{listener_status}")
def real_time_inference(listener_status:int):
    shard_id = 'shardId-000000000000' #we only have one shard!
shard_it = client.get_shard_iterator(StreamName="telemetry-power-consumption", ShardId=shard_id, \
    ShardIteratorType="LATEST")["ShardIterator"]
while 1==listener_status:
    out = client.get_records(ShardIterator=shard_it, Limit=2)
    shard_it = out["NextShardIterator"]
    print(out)
    time.sleep(5)
    
    
    
    return {"message": "success"}