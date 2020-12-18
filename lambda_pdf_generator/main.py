from fastapi import FastAPI
import boto3
import time
import json
from mangum import Mangum
from PyPDF2 import PdfFileWriter as w
import fitz

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

app = FastAPI(root_path = "/prod")

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

@app.get("/")
async def root():
    return {"message": "stream splitter"}

@app.get("/pdf_from_image/userid/{userid}")
async def pdf_from_images(userid: int):

    pdf=w()
    file=open("/tmp/input.pdf","wb")
    for i in range(4):
        pdf.addBlankPage(219,297) #a4 size dimensions
    pdf.write(file)
    file.close()
    
    input_file = "/tmp/input.pdf"

    # download images to tmp file
    my_bucket = s3.Bucket("usage-hist-stream")
    objects_to_download = []
    for object_summary in my_bucket.objects.filter(Prefix='output/' + str(userid)):
        print('Found file %s' % object_summary.key)
        objects_to_download.append(object_summary.key)

    objects_to_download = objects_to_download[-5:]

    for file in objects_to_download:
    KEY = file
    local_path = '/tmp/' + file.split('/')[-1]
    try:
        s3.Bucket('usage-hist-stream').download_file(KEY, local_path)
        print('downloaded file ' + file)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    output_file = "/tmp/output.pdf"
    image_file1 = "/tmp/image1.png"
    image_file2 = "/tmp/image2.png"
    image_file3 = "/tmp/image3.png"
    image_file4 = "/tmp/image4.png"
    f = open('/tmp/text.txt')
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

    return {'message': 'success',
            'url': response}

handler = Mangum(app)
