from fastapi import FastAPI
from bs4 import BeautifulSoup
import re
# from urllib.request import Request, urlopen
import requests
import boto3
from botocore.exceptions import NoCredentialsError
from typing import Optional
import hashlib
import base64
import logging
import threading
import uuid
# from botocore.vendored import requests
import json,os



ACCESS_KEY = 'AKIAW6VXUO4OULN7JM4K'
SECRET_KEY = '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'

app = FastAPI()

# specify the url
quote_page = 'https://seekingalpha.com/earnings/earnings-call-transcripts'
# req = Request(quote_page, headers={'User-Agent': 'Mozilla/5.0'})
# webpage = urlopen(req).read()
page = requests.get(quote_page)
webpage = page.text
# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(webpage, 'html.parser')
# Take out the <tag> of name and get its value
name_box = soup.find_all('li', attrs={'class': 'list-group-item article'})

# Create a dictionary with company name -> endpoint/route for
# an article 
call_list = {}
for idx,ele in enumerate(name_box):
    link_to_company = ele.find('a', attrs={'class': 'dashboard-article-link'})
    m = re.search(r'^[^\)]+', link_to_company.text.strip())
    company = m.group(0) + ')'
    call_list[company] = link_to_company['href']

site_prefix = 'https://seekingalpha.com'

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

#supporting functions

ddb = boto3.client('dynamodb',
                    aws_access_key_id="AKIAIGBTOQC5574I3CMA",
                    aws_secret_access_key="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")

def timeout(event, context):
    raise Exception('Execution is about to time out, exiting...')
    
def addText2dict(text,entity):
    entity["Text"] = text[entity['BeginOffset']:entity['EndOffset']]
    return entity

def add_text(text,entity_list):
    return [addText2dict(text,entity) for entity in entity_list]
    
    

    
def store_deidentified_message(message, entity_map, ddb_table):
    hashed_message = hashlib.sha3_256(message.encode()).hexdigest()
    for entity_hash in entity_map:
        ddb.put_item(
            TableName=ddb_table,
            Item={
                'MessageHash': {
                    'S': hashed_message
                },
                'EntityHash': {
                    'S': entity_hash
                },
                'Entity': {
                    'S': entity_map[entity_hash]
                }
            }
        )
    return hashed_message
    
def deidentify_entities_in_message(message, entity_list):
    entity_map = dict()
    for entity in entity_list:
      salted_entity = entity['Text'] + str(uuid.uuid4())
      hashkey = hashlib.sha3_256(salted_entity.encode()).hexdigest()
      entity_map[hashkey] = entity['Text']
      message = message.replace(entity['Text'], hashkey)
    return message, entity_map

# Connect to S3
s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id='AKIAW6VXUO4OULN7JM4K', 
    aws_secret_access_key='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'
    )

def read_file(s3_key):
    s3 = boto3.client('s3')

    print ('Getting file %s..' % s3_key)
    obj = s3.get_object(Bucket="earnings-call-scraped", Key=s3_key)
#     df = pd.read_csv(io.BytesIO(obj['Body'].read()))
#     body = io.BytesIO(obj['Body'].read().decode(encoding="utf-8",errors="ignore"))
    body = obj['Body'].read().decode(encoding="utf-8",errors="ignore")
    return body

def read_file_json(s3_key):
    s3 = boto3.client('s3')

    print ('Getting file %s..' % s3_key)
    obj = s3.get_object(Bucket="earnings-call-scraped", Key=s3_key)
    body = obj['Body'].read().decode(encoding="utf-8",errors="ignore")
    content_json = json.loads(body)
    return content_json

@app.get("/")
async def root():
    return {"message": "Scraper test"}

@app.get("/companyName/{company_name}", tags=['Scrape Earnings Call'])
def scrape_earnings_call(company_name: str):
    site_postfix = call_list[company_name]  
    # full url for the current link being scraped
    site_url = site_prefix + site_postfix
    # Enter the link to scrape data
    # scrape_earnings_call = Request(site_url, headers={'User-Agent': 'Mozilla/5.0'})       
    # earnings_call_webpage = urlopen(scrape_earnings_call).read()
    page = requests.get(site_url)
    earnings_call_webpage = page.text
    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(earnings_call_webpage, 'html.parser')     
    # get a list of paragraph <p> tags text content, in this website
    # they are of the format 'p p1', 'p p2'.. 'p pn'
    p_list = ['p p' + str(i) for i in range(1,20+1)]  
    with open(str(company_name) + '_scraped_data.txt', 'w') as f:
        for p in p_list:
            name_box = soup.find_all('p', attrs={'class': p})
            for i in name_box:
                f.write(i.text)
                f.write('\n')

        uploaded = upload_to_aws(str(company_name) + '_scraped_data.txt', 'earnings-call-scraped', str(company_name) + '_scraped_data.txt')
    return 'Scraped file ' + str(company_name) + '_scraped_data.txt' + ' successfully uploaded to S3'
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/pii_entities/{text}")
def detect_pii_entities(text: str):
    client = boto3.client('comprehend')
    my_bucket = s3.Bucket("comprehend-bucket-asmt2")

    response = client.detect_pii_entities(
        Text=text,
        LanguageCode='en'
    )
    
    return response


@app.get("/pii_entities_s3/{company_name}/limit_characters/{char_limit}", tags=['NER'])
def detect_pii_entities_s3(company_name: str, char_limit: str):
    
    client = boto3.client('comprehend')
    my_bucket = s3.Bucket("earnings-call-scraped")
    for object_summary in my_bucket.objects.filter(Prefix=company_name):
        print('Found file %s' % object_summary.key)
        # print(read_file(object_summary.key))
        text = read_file(object_summary.key)
    try:
        response = client.detect_pii_entities(
            Text=text[:int(char_limit)],
            LanguageCode='en'
        )

        s3.Object('earnings-call-scraped', 'entities/{}.json'.format(company_name)).put(Body=json.dumps(response))
        print("successfully uploaded entities for {}".format(company_name))
    except Exception as e:
        print("error message -->",e)
        print("No text acquired from S3")
    
    
    return response

@app.get("/deidentify/")
def deidentiy():
    client = boto3.client('comprehend')
    my_bucket = s3.Bucket("comprehend-bucket-asmt2")

    for object_summary in my_bucket.objects.filter(Prefix="input/redact/input"):
        print('Found file %s' % object_summary.key)
    #     print(read_file(object_summary.key))
        text = read_file(object_summary.key)
        entity_list = detect_pii_entities(text)['Entities']
        entity_list = add_text(text,entity_list)
        deidentified_message, entity_map = deidentify_entities_in_message(text, entity_list)
        hashed_message = store_deidentified_message(deidentified_message, entity_map, "DeidentificationTable")
        
        return deidentified_message

