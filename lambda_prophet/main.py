
import boto3
import json,io
from fbprophet.serialize import model_to_json, model_from_json
import pandas as pd
from fbprophet import Prophet
import datetime
import matplotlib.pyplot as plt


from fastapi import FastAPI


app = FastAPI()

def gen_datetime(datetime_str):
    """
    input: datetime string : format example -> '2010-11-02 21:00:00'
    
    returns dataframe containing date points till the end of the month
    """
    numdays = 30
    try:
        base = datetime.datetime.strptime(datetime_str,'%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print("The datetime format is not correct",e)
        return pd.DataFrame()
    dates = [str((base + datetime.timedelta(days=x)))  for x in range(numdays) 
                 if (base + datetime.timedelta(days=x)).month == base.month]
    return pd.DataFrame(dates, columns=["ds"])


BUCKET = 'sagemaker-model-7245'

    
def get_model(bucket = 'sagemaker-model-7245',model_path = 'prophet_model.json'): 
    """
    inputs: 
    bucket name
    model_path
    
    output:
    returns FB prophet model stored in S3
    """
    client = boto3.client('s3',
                           aws_access_key_id='AKIAIGBTOQC5574I3CMA',
                           aws_secret_access_key='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'
                         )
    result = client.get_object(Bucket=BUCKET, Key=model_path) 
    text = result["Body"].read().decode('utf-8')

    return model_from_json((json.loads(text)))


def save_plot_s3(fig, KEY,BUCKET_NAME = 'sagemaker-model-7245'):
    
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png')
    img_data.seek(0)

    session = boto3.Session(
        aws_access_key_id='AKIAIGBTOQC5574I3CMA',
        aws_secret_access_key='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',
        region_name='us-east-2'
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.put_object(Body=img_data, ContentType='image/png', Key=KEY)
    print("Successfully saved plot {} to S3".format(KEY))





@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/monthly_prediction/{datetime_str}")
def prophet_predict(datetime_str: str):
    #instantiate prophet model from s3
    m = get_model()
    
    bucket_name = 'sagemaker-model-7245'
    #generate dates till end of the month
    dates_df = gen_datetime(datetime_str)
    
    #get predictions till end of the month
    forecast = m.predict(dates_df)
    
    
    #plot fig1
    fig1 = plt.figure()
    plt.plot(dates_df['ds'], forecast['yhat'])
    _ = plt.xticks(rotation=90)
    
    save_plot_s3(fig=fig1, BUCKET_NAME = bucket_name, KEY = datetime_str+'/fig1.png')
    
    #plot fig2
    fig2 = m.plot_components(forecast)
    save_plot_s3(fig=fig2, BUCKET_NAME = bucket_name, KEY = datetime_str+'/fig2.png')
    
    return {'predictions':forecast[['ds','yhat']], 
           'datetime_str': datetime_str,
           'bucket': bucket_name}


