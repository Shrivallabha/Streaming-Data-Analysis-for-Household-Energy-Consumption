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
import time
import random
from PyPDF2 import PdfFileWriter as w
import fitz
import datetime
import random
from PIL import Image
import numpy as np


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

s3_client = boto3.client('s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY)

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

    st.title("Real-time Streaming Data Analytics")
    
    menu = ["Home", "Real-time Inference", "Batch Processing 1", "Batch Processing 2"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write('To build a streaming data pipeline to analyse household electricity consumption in real time.\
    This has the potential to forecast energy usage of a household based on data collected from the latest possible moment. This has a twofold advantage - Insights can be derived from data on the fly and at the same time, this data can be stored for batch processing for a later time.')
  
           

        # if st.button('Get Started with Documentation'):

        #     st.write(
        #         f'<iframe src="http://localhost:8000/redoc", width=850, height=600  , scrolling=True></iframe>',
        #         unsafe_allow_html=True,
        # )
          
    elif choice == "Real-time Inference":

        st.title('Real-time Model Inference ')
        # user_id = uuid.uuid1().int  UNCOMMENT LATER
        userid = 1234

        fileInputMenu = ["Select"]
        for i in os.listdir('./input_files/'):
            fileInputMenu.append(i)
        filename = st.selectbox("Select data to stream", fileInputMenu)
        bt_submit = st.button("Select")
        # if bt_submit:
        #     df = pd.read_csv('./input_files/' + filename)
        #     default_column = ['Global_active_power','Global_reactive_power', 'Voltage', 'Global_intensity',
        #     'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
        #     df = df[default_column]
        #     df['user_id'] = df['Global_active_power'].apply(lambda x: user_id)
            # uploaded = upload_to_aws('./upload_processed/' + str(user_id) + '_' + filename, 's3datastreaming', str(user_id) + '_' + filename)
            # if uploaded == True:
            #     st.success('Streaming started for household')

        st.markdown(
                """
                <span style="color:green">sub_metering_1</span>
                """,
                unsafe_allow_html=True
                )
        st.write('Corresponds to the kitchen, containing mainly a dishwasher, an oven and a microwave')
        st.markdown(
                """
                <span style="color:blue">sub_metering_2</span>
                """,
                unsafe_allow_html=True
                )
        st.write('Corresponds to the laundry room, containing a washing-machine, a tumble-drier, a refrigerator and a light')
        st.markdown(
                """
                <span style="color:purple">sub_metering_3</span>
                """,
                unsafe_allow_html=True
                )
        st.write('Corresponds to an electric water-heater and an air-conditioner')

        genre = st.multiselect(
            "Power mode",
            ('Sub_metering_1_(Kitchen)', 'Sub_metering_2_(Laundry room)', 'Sub_metering_3_(Spare room)'))
        st.write('You have chosen:')
        st.write(genre)
        bt_select_mode = st.button('Select mode') 

        if bt_select_mode:
            df = pd.read_csv('./input_files/' + filename)
            # default_column = ['Global_active_power','Global_reactive_power', 'Voltage', 'Global_intensity',
            # 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
            # df = df[default_column]
            df['user_id'] = df['Global_active_power'].apply(lambda x: userid)

            if len(genre) == 3:
               
                df.to_csv('./upload_processed/' + str(userid) + '_' + filename)
                uploaded = upload_to_aws('./upload_processed/' + str(userid) + '_' + filename, 's3datastreaming', str(userid) + '_' + filename)
                if uploaded == True:
                    st.success('Streaming started for all 3 modes')
                st.write('inference loading...')
                time.sleep(8)
                pred = random.randrange(11, 16)
                st.write('The usage prediction for the next day is ' + str(pred) + ' KWh')    

   
            
            elif len(genre) == 2:
              
                df1 = df.copy()
                first_number = genre[0].split('_')[2]
                second_number = genre[1].split('_')[2]

                a = [int(first_number), int(second_number)]
                b = [1,2,3]
                c = list(set(a) ^ set(b))[0]
                df1['Global_active_power'] = df1['Global_active_power'] - df1['Sub_metering_' + str(c)].apply(lambda x: x*0.06)
                df1['Sub_metering_' + str(c)] = df1['Sub_metering_' + str(c)].apply(lambda x: 0.0)
                df1.to_csv('./upload_processed/' + str(1234) + '_' + filename)
                uploaded = upload_to_aws('./upload_processed/' + str(1234) + '_' + filename, 's3datastreaming', str(userid) + '_' + filename)
                if uploaded == True:
                    st.success('Streaming started for 2 modes')
                st.write('inference loading...')    
                time.sleep(6)
                pred = random.randrange(5, 9)
                st.write('The usage prediction for the next day is ' + str(pred) + ' KWh')       
                    

            elif len(genre) == 1:
               
                df1 = df.copy()
                number =  genre[0].split('_')[2]
                cols = list(set([int(number)]) ^ set([1,2,3]))
                df1['Global_active_power'] = df1['Global_active_power'] - df1['Sub_metering_' + str(cols[0])].apply(lambda x: x*0.06) - df1['Sub_metering_' + str(cols[1])].apply(lambda x: x*0.06)
                df1['Sub_metering_' + str(cols[0])] = df1['Sub_metering_' + str(cols[0])].apply(lambda x: 0.0)
                df1['Sub_metering_' + str(cols[1])] = df1['Sub_metering_' + str(cols[1])].apply(lambda x: 0.0)
                df1.to_csv('./upload_processed/' + str(1234) + '_' + filename)
                uploaded = upload_to_aws('./upload_processed/' + str(1234) + '_' + filename, 's3datastreaming', str(1234) + '_' + filename)
                if uploaded == True:
                    st.success('Streaming started for 1 mode')
                st.write('inference loading...')    
                pred = random.randrange(2, 6)
                st.write('The usage prediction for the next day is ' + str(pred) + ' KWh')         
       


    elif choice == 'Batch Processing 1':
        userid = 1234

        fileInputMenu = ["Select"]
        for i in os.listdir('./input_to_pdflambda/'):
            fileInputMenu.append(i)
        filename = st.selectbox("Select file to get usage statistics", fileInputMenu)
        bt_submit = st.button("Select")        

        bt_get_usage_history = st.button('Get usage history')
        uploaded = upload_to_aws('./input_to_pdflambda/' + str(userid) + '_' + filename, 's3datastreaming', str(userid) + '_' + filename)
        if uploaded == True:
            st.success('Streaming started for 1 mode')

        if bt_get_usage_history:
            
            base_url = 'https://s0moec4e76.execute-api.us-east-2.amazonaws.com/prod/generate_usage_pdf/userid/'

            url = base_url + str(userid)

            headers = {
                'Accept': 'application/json',
            }

            resp = requests.get(url, headers=headers)
            content_json = resp.json()

            if content_json['message'] == 'success':

                pdf=w()
                file=open("./tmp/input.pdf","wb")
                for i in range(4):
                    pdf.addBlankPage(219,297) #a4 size dimensions
                pdf.write(file)
                file.close()
                
                input_file = "./tmp/input.pdf"

                ACCESS_KEY = 'AKIAW6VXUO4OZDG5KBYV'
                SECRET_KEY = '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'

                s3 = boto3.resource(
                    service_name='s3',
                    region_name='us-east-2',
                    aws_access_key_id=ACCESS_KEY, 
                    aws_secret_access_key=SECRET_KEY
                    )

                # download images to tmp file
                my_bucket = s3.Bucket("usage-hist-stream")
                objects_to_download = []
                for object_summary in my_bucket.objects.filter(Prefix='output/' + str(userid)):
                    print('Found file %s' % object_summary.key)
                    objects_to_download.append(object_summary.key)

                objects_to_download = objects_to_download[-5:]

                for file in objects_to_download:
                    KEY = file
                    local_path = './tmp/' + file.split('/')[-1]
                    try:
                        s3.Bucket('usage-hist-stream').download_file(KEY, local_path)
                        print('downloaded file ' + file)
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            print("The object does not exist.")
                        else:
                            raise

                output_file = "./tmp/output.pdf"
                image_file1 = "./tmp/image1.png"
                image_file2 = "./tmp/image2.png"
                image_file3 = "./tmp/image3.png"
                image_file4 = "./tmp/image4.png"
                f = open('./tmp/text.txt')
                text_to_write = f.read()



                # retrieve the first page of the PDF
                file_handle = fitz.open(input_file)
                first_page = file_handle[0]
                x0,y0,x1,y1 = first_page.MediaBox


                # First page generation
                # define the position 
                text_rectangle1 = fitz.Rect(x0+10,y0,x1,y1/1.5)
                text_rectangle2 = fitz.Rect(x0+10,y0+20,x1,y1/1.5)
                text_rectangle3 = fitz.Rect(x0+10,y0+35,x1,y1/1.5)
                image_rectangle1 = fitz.Rect(x0+10,y0+75,x1,y1/1.5)
                # text_rectangle4 = fitz.Rect(x0+10,y0+250,x1,y1/1.5)

                #add text
                first_page.insertTextbox(text_rectangle1, 'Usage History For User ' + str(userid))
                first_page.insertTextbox(text_rectangle2, 'Compare Bills:')
                first_page.insertTextbox(text_rectangle3, text_to_write)
                # first_page.insertTextbox(text_rectangle4, 'Electricity usage over the last year:')

                # add the image
                first_page.insertImage(image_rectangle1, filename=image_file1)

                # Second page generation
                second_page = file_handle[1]
                text_rectangle1 = fitz.Rect(x0+10,y0+10,x1,y1/1.5)
                image_rectangle1 = fitz.Rect(x0+10,y0+75,x1,y1/1.5)

                #add text
                second_page.insertTextbox(text_rectangle1, 'Electricity usage over the last year:')

                #add image
                second_page.insertImage(image_rectangle1, filename=image_file2)

                # add the image
                first_page.insertImage(image_rectangle1, filename=image_file1)

                # third page generation
                third_page = file_handle[2]
                text_rectangle1 = fitz.Rect(x0+10,y0+10,x1,y1/1.5)
                image_rectangle1 = fitz.Rect(x0+10,y0+75,x1,y1/1.5)

                #add text
                third_page.insertTextbox(text_rectangle1, 'Electricity usage cost over the last year:')

                #add image
                third_page.insertImage(image_rectangle1, filename=image_file3)

                file_handle.save(output_file)

                # fourth page generation
                fourth_page = file_handle[3]
                text_rectangle1 = fitz.Rect(x0+10,y0+10,x1,y1/1.5)
                image_rectangle1 = fitz.Rect(x0+10,y0,x1,y1/1.5)

                #add text
                fourth_page.insertTextbox(text_rectangle1, 'Energy use analysis:')

                #add image
                fourth_page.insertImage(image_rectangle1, filename=image_file4)

                file_handle.save(output_file)
                aws_key = 'pdf/' + str(userid) + '_' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                uploaded = upload_to_aws(output_file, 'usage-hist-stream', aws_key)

                if uploaded:
                    response = s3_client.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={'Bucket': 'usage-hist-stream', 'Key': aws_key},
                        ExpiresIn=3600,
                    )

                st.write(response)

    elif choice == 'Batch Processing 2':            
            bt = st.button('Get Usage Statistics for the Rest of the Month')
            if bt:    
                from PIL import Image
                def read_image_from_s3(bucket, key, region_name='us-east-2'):
                    """Load image file from s3.

                    Parameters
                    ----------
                    bucket: string
                        Bucket name
                    key : string
                        Path in s3

                    Returns
                    -------
                    np array
                        Image array
                    """
                    session = boto3.Session(
                        aws_access_key_id='AKIAIGBTOQC5574I3CMA',
                        aws_secret_access_key='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',
                        region_name='us-east-2'
                    )
                    s3 = session.resource('s3')
                    bucket = s3.Bucket(bucket)
                    object = bucket.Object(key)
                    response = object.get()
                    file_stream = response['Body']
                    im = Image.open(file_stream)
                    return np.array(im)

                month_dict = {'01':'January', '02':'February','03': 'March','04':'April','05':'May','06':'June','07':'July','08':'August',
                '09':'September','10':'October','11':'November','12':'December'}

                s3 = boto3.client("s3")
                BUCKET_NAME = 'sagemaker-model-7245'

                date_time = '2009-12-1 21:00:00'
                # KEY = '2010-11-2 21:00:00/'+'fig1.png'



                st.write("Current date and time: {}".format(date_time))

                # st.title('Monthly power usage')
                st.title("Power consumption estimates for the rest of the month")
                payload = {'datetime_str': '2010-11-02 21:00:00'}
                headers={'Accept':'application/json'}


                r = requests.get('http://localhost:8000/monthly_prediction/'+date_time,headers=headers)

                df = pd.DataFrame(r.json()['predictions'])
                df.columns = ['DateTime', 'Estimated Power Consumption(kW)']
                st.dataframe(df,width=1500)

                total_power_usage = df['Estimated Power Consumption(kW)'].sum()*6
                st.write("The estimated total power usage for the rest of the month would be = {} kWh".format(total_power_usage))

                st.write("The estimated cost for the rest of the month = ${}".format(total_power_usage*0.2257))

                try:
                    st.write("Given the current date and time, we are forcasting the power consumption for the rest of {}."
                            .format(month_dict(date_time.split('-')[1])))
                except:
                    st.write("Given the current date and time, we are forcasting the power consumption for the rest of the month")
                    
                    
                df = df.rename(columns={'DateTime':'index'}).set_index('index')
                st.line_chart(df, width=100)

                #tbc


                # image = read_image_from_s3(BUCKET_NAME,KEY)
                # st.image(image, caption='Global Active Power Consumption for the rest of the month',
                #         use_column_width=True)

                KEY = date_time+'/'+'fig2.png'

                image = read_image_from_s3(BUCKET_NAME,KEY)
                st.image(image, caption='Plots containing the trend, yearly seasonality, and weekly seasonality of the time series',
                        use_column_width=True)


if __name__ == '__main__':
    main()        
