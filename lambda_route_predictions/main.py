from fastapi import FastAPI
import boto3
import time
import json
import pandas as pd
from mangum import Mangum
import random
import uuid
import numpy as np
import datetime as dt


ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
SECRET_KEY = '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'

client = boto3.client(
    'kinesis',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

def predict(data):

    cols = ['Global_active_power',
       'Global_reactive_power', 'Voltage', 'Global_intensity',
       'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
    data = data[cols]   
    
    data = data.resample('h').mean()
    client = boto3.client('sagemaker-runtime', 
                         aws_access_key_id='AKIAIGBTOQC5574I3CMA',
                        aws_secret_access_key='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')
    endpoint_name = 'tensorflow-inference-2020-12-18-12-07-04-982'  
    
    min_ = np.array([1.73818056e-01, 5.78111111e-02, 2.31088229e+02, 8.08333333e-01,
       0.00000000e+00, 0.00000000e+00, 8.94444444e-01])
    range_ = np.array([ 3.14103333,  0.23235139, 16.34677778, 13.21972222,  7.76327911,
            8.40902778, 15.59375   ])
    
    values = data.values
    # print(values)
    #load scaler
#     scaler=load(scaler_path)
#     scaled = scaler.transform(values)
#     print(scaled)
    scaled = (values-min_)/range_
    
#     print(scaled.shape)
    

#     print(np.reshape(scaled,(scaled.shape[0],1,scaled.shape[1])).shape)
    
    payload =   {"instances": np.reshape(scaled,(scaled.shape[0],1,scaled.shape[1])).tolist()} 

    response = client.invoke_endpoint(
        EndpointName=endpoint_name, 
        ContentType='application/json',
        Body=json.dumps(payload)
        )
    
    preds = json.loads(response['Body'].read().decode('utf-8'))
    predictions = preds['predictions']

#     print(len(predictions))
    inv_yhat = np.concatenate((predictions, scaled[:, -6:]), axis=1)
#     inv_yhat = scaler.inverse_transform(inv_yhat)
    inv_yhat = inv_yhat*range_+min_

    inv_yhat = inv_yhat[:,0]
    return inv_yhat


# Function to upload file to s3
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False



def load2table(item):
    resource = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id='AKIAW6VXUO4OZDG5KBYV', aws_secret_access_key='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')
    table = resource.Table("real-time-predictions")

    table.put_item(Item=item)
    print("credentials loaded to dynamoDB.")   

app = FastAPI(root_path = "/prod")


@app.get("/")
async def root():
    return {"message": "stream splitter"}

@app.get("/split_stream/")
async def get_stream_by_userid():
    shard_id = 'shardId-000000000000' #we only have one shard!
    shard_it = client.get_shard_iterator(StreamName="telemetry-power-consumption", ShardId=shard_id, \
        ShardIteratorType="LATEST")["ShardIterator"]
    # t_end = time.time() + 200
    # while time.time()<t_end:
    while 1==1:    
        out = client.get_records(ShardIterator=shard_it, Limit=10)
        if out['Records']:
            group_records = []
            df = pd.DataFrame()
            for record in out['Records']:
                sample = json.loads(record['Data'])
                df_to_append = pd.json_normalize(sample)
                df = df.append(df_to_append)
            df['dt'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            df = df.set_index('dt')   
            prediction = predict(df)
            prediction_key = uuid.uuid1()
            content_dict = {'user_id': str(df.iloc[-1].user_id), 'prediction': str(prediction), 'prediction_id':str(prediction_key)}
            filename = str(1234) + '_' + str(prediction[0]) + '_' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f = open('/tmp/sample.txt', 'wb')
            f.close()
            uploaded = upload_to_aws('/tmp/sample.txt', 'usage-hist-stream', 'predictions/' + filename)
            load2table(content_dict)
        shard_it = out["NextShardIterator"]
        print(out)
        print('\n')
        time.sleep(5)
    
    return {'message': 'success'}

handler = Mangum(app)
