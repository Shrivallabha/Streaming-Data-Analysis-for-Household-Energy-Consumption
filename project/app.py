import streamlit as st
import boto3
import pandas as pd
import requests
import re
import json
import boto
from boto.s3.key import Key
import boto.s3.connection
import requests
import base64
import uuid
import tkinter as tk  
import os

AWS_ACCESS_KEY_ID = 'AKIAW6VXUO4OZDG5KBYV'
AWS_SECRET_ACCESS_KEY = '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'

ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
SECRET_KEY = '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'

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY
    )

def read_file(s3_key):
    s3 = boto3.client('s3')

    print ('Getting file %s..' % s3_key)
    obj = s3.get_object(Bucket="earnings-call-scraped", Key=s3_key)
    body = obj['Body'].read().decode(encoding="utf-8",errors="ignore")
    return body

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def serialize_text(text):
    example = tf.train.Example(features=tf.train.Features(feature={
        'text': _bytes_feature(text)
        }))
    serialized_example = example.SerializeToString()
    return serialized_example

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
    except NoCredentialsError:
        print("Credentials not available")
        return False


def main():
    """
    Model as a Service
    """

    st.title("Streaming data analysis")

    menu = ["Home", "User logged in"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":

        st.write('Enter description'
                )    
           

        # if st.button('Get Started with Documentation'):

        #     st.write(
        #         f'<iframe src="http://localhost:8000/redoc", width=850, height=600  , scrolling=True></iframe>',
        #         unsafe_allow_html=True,
        # )
          
    if choice == "User logged in":
        st.write('logged in')
        # user_id = uuid.uuid1().int  UNCOMMENT LATER
        user_id = 1234

        fileInputMenu = ["Select"]
        for i in os.listdir('./input_files/'):
            fileInputMenu.append(i)
        filename = st.selectbox("Choose streaming data to upload", fileInputMenu)
        bt_submit = st.button("Submit")
        df = pd.read_csv('./input_files/' + filename)
        default_column = ['Date', 'Time', 'Global_active_power','Global_reactive_power', 'Voltage', 'Global_intensity',
        'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
        df = df[default_column]
        df['user_id'] = df['Date'].apply(lambda x: user_id)
        df.to_csv('./upload_processed/' + str(user_id) + '_' + filename)
        if bt_submit:
            uploaded = upload_to_aws('./upload_processed/' + str(user_id) + '_' + filename, 's3datastreaming', str(user_id) + '_' + filename)
            if uploaded == True:
                st.success('Streaming started for household')


        bt_see_usage = st.button('See current usage')    

        if bt_see_usage:
            pass

  


      

if __name__ == '__main__':
    main()        
