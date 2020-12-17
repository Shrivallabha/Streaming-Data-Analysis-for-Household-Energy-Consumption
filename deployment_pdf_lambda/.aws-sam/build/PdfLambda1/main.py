import boto3
import pandas as pd
import time
import json
from fastapi import FastAPI
from mangum import Mangum
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os

ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
SECRET_KEY = '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'

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY
    )

s3_client = boto3.client('s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY)

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

calender = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', \
           7:'July', 8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

def return_plot_image(labels, values, y_label, title):
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    
    fig, ax = plt.subplots(figsize=(10, 5))
    rects = ax.bar(x - width/2, values, width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    fig.tight_layout()
    
    return fig

app = FastAPI(root_path = "/prod")


@app.get("/")
async def root():
    return {"message": "pdf generation"}

@app.get("/generate_usage_pdf/userid/{userid}")
async def generate_usage_pdf(userid: int):
    
    my_bucket = s3.Bucket("usage-hist-stream")

    for object_summary in my_bucket.objects.filter(Prefix=str(userid)):
        print('Found file %s' % object_summary.key)
        file = s3_client.download_file("usage-hist-stream", str(object_summary.key), '/tmp/input_file')
    
    df = pd.read_csv('/tmp/input_file', parse_dates=['Date'])
    if len(df.Date.dt.month.unique()) < 2:
        return {'message': 'not enough data available'}
    current_year = df.iloc[-1].Date.year
    df = df[df.Date.dt.year == current_year]
    df = df.dropna()
    cols = df.columns.drop(['Date', 'Time'])
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    df['Global_active_power'] = df['Global_active_power'].apply(lambda x: x*1000/60)

    # Compare bills
    # detect current month in the dataset
    current_month = df.iloc[-1].Date.month
    prev_month = current_month - 1
    monthly_usage = df.groupby([df.Date.dt.year, df.Date.dt.month]).sum()['Global_active_power']
    monthly_usage_kwh = (monthly_usage/1000)
    monthly_usage_kwh = list(monthly_usage_kwh)
    current_usage = monthly_usage_kwh[-1]
    prev_usage = monthly_usage_kwh[-2]

    labels = [calender[prev_month], calender[current_month]]
    values = [round(prev_usage,2), int(round(current_usage))]

    y_label = 'Energy usage (KWh)'
    title = 'Energy usage for the last two months'

    fig = return_plot_image(labels, values, y_label, title)
    # user folder
    fig.savefig('/tmp/image1.png')

    diff = (prev_usage - current_usage)
    if diff < 0:
        text_to_write = f'You have used {round(-diff,2)} KWh more energy and spent ${round(-diff*0.2,2)} more on electricity than the last billing period.'
    elif diff > 0:
        text_to_write = f'You have used {round(diff,2)} KWh less energy and spent ${round(diff*0.2,2)} less on electricity than the last billing period.'
    else:
        text_to_write = f'You have used the same KWh energy and spent the same $ on electricity than the last billing period.'

    file = open("/tmp/text.txt", 'wb')
    file.write(text_to_write.encode('utf-8'))
    file.close()

    # Image 2

    monthly_usage = df.groupby([df.Date.dt.year, df.Date.dt.month]).sum()['Global_active_power']
    monthly_usage_kwh = (monthly_usage/1000)
    monthly_usage_kwh = list(monthly_usage_kwh)
    number_of_months = len(df.Date.dt.month.unique())

    labels = [calender[i] for i in range(1,number_of_months+1)]
    values = [int(i) for i in monthly_usage_kwh]

    y_label = 'Energy usage (KWh)'
    title = 'Energy usage over the last year'

    fig = return_plot_image(labels, values, y_label, title)

    fig.savefig('/tmp/image2.png')

    # Image 3

    labels = [calender[i] for i in range(1,number_of_months+1)]
    values = [int(i*0.2) for i in monthly_usage_kwh]

    y_label = 'Energy usage cost ($)'
    title = 'Energy usage cost over the last year'

    fig = return_plot_image(labels, values, y_label, title)

    fig.savefig('/tmp/image3.png')

    # Image 4

    # Circle chart
    monthly_usage = df.groupby([df.Date.dt.year, df.Date.dt.month]).sum()['Global_active_power']
    monthly_usage = monthly_usage/1000
    monthly_usage_divided = df.groupby([df.Date.dt.year, df.Date.dt.month]).sum()[['Global_active_power' ,'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']]
    monthly_usage_divided = monthly_usage_divided/1000
    sum_across_sub_meters = monthly_usage_divided.drop(['Global_active_power'], axis=1).sum(axis=1)
    monthly_usage_divided['Global_active_power'] = monthly_usage_divided['Global_active_power'] - sum_across_sub_meters

    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Rest of the house', 'Kitchen', 'Laundry Room', 'Hall'
    sizes = list(monthly_usage_divided.sum())
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots(figsize=(5,10))
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    fig1.savefig('/tmp/image4.png')

    # save all images to user folder
    prefix = 'output/' + str(1234) + '_' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    files_list = os.listdir('/tmp/')

    print('FILES LIST', files_list)
    
    for file in files_list:
        if file in ['image1.png', 'image2.png', 'image3.png', 'image4.png', 'text.txt']:
            uploaded = upload_to_aws('/tmp/' + str(file), 'usage-hist-stream', prefix + '/' + str(file))
        
    return {'message': 'success'}

handler = Mangum(app)
