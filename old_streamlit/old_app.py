import streamlit as st
import boto3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json

def load2table(username, r):
    resource = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id='AKIAIGBTOQC5574I3CMA', aws_secret_access_key='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')
    table = resource.Table("token-table")

    item = {"userName" : username,
           "AccessToken" : r['AccessToken'],
           "RefreshToken": r['RefreshToken'],
           "IdToken": r['IdToken']}

    table.put_item(Item=item)
    print("credentials loaded to dynamoDB.")
    
def sign_up_cognito(ci,upi,user,pwd):
    cidp = boto3.client('cognito-idp')

    cidp.sign_up(
        ClientId= ci,
        Username= user,
        Password= pwd)
                                                                          
    cidp.admin_confirm_sign_up(
        UserPoolId= upi,
        Username= user)

    r = cidp.admin_initiate_auth( #first login 
        UserPoolId= upi,
        ClientId= ci,
        AuthFlow= "ADMIN_NO_SRP_AUTH",
        AuthParameters= {
        "USERNAME": user,
        "PASSWORD": pwd
        })   
        
    m = cidp.admin_initiate_auth( #further logins
        UserPoolId= upi,
        ClientId= ci,
        AuthFlow= "REFRESH_TOKEN_AUTH",
        AuthParameters= {
        "REFRESH_TOKEN" : r["AuthenticationResult"]["RefreshToken"]
        })
    load2table(username = user, r = r['AuthenticationResult'])
    return(r["AuthenticationResult"]['IdToken'])
     
def read_file_json(s3_key):
    s3 = boto3.client('s3')

    print ('Getting file %s..' % s3_key)
    obj = s3.get_object(Bucket="earnings-call-scraped", Key=s3_key)
    body = obj['Body'].read().decode(encoding="utf-8",errors="ignore")
    content_json = json.loads(body)
    return content_json

ACCESS_KEY = 'AKIAW6VXUO4OULN7JM4K'
SECRET_KEY = '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'

s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id=ACCESS_KEY, 
    aws_secret_access_key=SECRET_KEY
    )

def main():
    """
    simple login app
    """
    # Get company list to display

    # specify the url
    # quote_page = 'https://seekingalpha.com/earnings/earnings-call-transcripts'
    # # req = Request(quote_page, headers={'User-Agent': 'Mozilla/5.0'})
    # # webpage = urlopen(req).read()
    # page = requests.get(quote_page)
    # webpage = page.text
    # # parse the html using beautiful soup and store in variable `soup`
    # soup = BeautifulSoup(webpage, 'html.parser')
    # # Take out the <tag> of name and get its value
    # name_box = soup.find_all('li', attrs={'class': 'list-group-item article'})

    # # Create a dictionary with company name -> endpoint/route for
    # # an article 
    # call_list = {}
    # for idx,ele in enumerate(name_box):
    #     link_to_company = ele.find('a', attrs={'class': 'dashboard-article-link'})
    #     m = re.search(r'^[^\)]+', link_to_company.text.strip())
    #     company = m.group(0) + ')'
    #     call_list[company] = link_to_company['href']



    st.title("CSYE 7245 - De-Identification using Amazon Comprehend")

    menu = ["Home", "SignUp", 'API-1', 'API-2', 'API-3']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("The registered user is added to the userpool and is returned with a private key to\
                    access the API endpoints. The key is also stored in a DynamoDB table")
           
    elif choice == "SignUp":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("SignUp"):
            st.success("{} signed up successfully!".format(username))
            try:
                kid = sign_up_cognito("72qf8jgncdmbq0l1hq3ovnps3t","us-east-2_sa8eVZxAM",username,password)
                st.subheader("Private key generated successfully.")
                # st.subheader(kid)
                if kid:
                    st.markdown(kid)
                # if st.button('Download'):
                #     st.success("Download Started")
                #     s = pd.Series([kid])
                #     csv = s.to_csv('private_key.csv', index=False)



            except:
                pass    

    elif choice == "API-1":
        # Title of page
        st.title("Scrape Earnings Call")

        # s = st.State()
        fileInputMenu = ["Select"]
        # for i in call_list.keys():
        #     fileInputMenu.append(i) 
        filename = st.selectbox("Select Company to scrape Earnings Call", fileInputMenu)
        bt_submit = st.button("Submit")

        if ((bt_submit) and (filename != "Select")): # MAKE THIS ==
            st.error("Please select a Valid filename")
            # st.write("Error")
        elif ((bt_submit) and (filename == "Select")): # MAKE THIS != LATER
            #Data scrapping process
            filename = 'HP Inc. (HPQ)' # DELETE LINE LATER AFTER TEST

            #API 1
            base_url = 'http://localhost:8000/companyName/'
            url = base_url + filename
            resp = requests.get(url)
            if(resp.status_code == 200):
                st.markdown(
                """
                <span style="color:green">STATUS CODE 200</span>
                """,
                unsafe_allow_html=True
                )

                st.text(resp.content)
                st.text(resp.headers)

            else:
                st.markdown(
                """
                <span style="color:red">STATUS CODE 400</span>
                """,
                unsafe_allow_html=True
                )
                
                st.text(resp.content)
                st.text(resp.headers)
        


        while st.button('Read Documentation'):

            st.write(
                f'<iframe src="http://localhost:8000/redoc", width=850, height=600  , scrolling=True></iframe>',
                unsafe_allow_html=True,
        )

    elif choice == 'API-2':
        
        st.title("Named Entity Recognition")
        # st.write("Please select the entities to be recognized")

        # for i in call_list.keys():
        #     fileInputMenu.append(i)         

        fileInputMenu = ["Select"]
        filename = st.selectbox("Company Name", fileInputMenu)

        get_char = st.text_input('Character limit')



        filename = 'HP Inc. (HPQ)'

        base_url = 'http://localhost:8000/pii_entities_s3/'
        company_name = 'HP Inc. (HPQ)/'
        limit_url = 'limit_characters/'
        char = '500'

        url = base_url + company_name + limit_url + char

        if (st.button('Submit')):

            resp = requests.get(url)
            content_json = resp.json()

            if(resp.status_code == 200):
                    st.markdown(
                    """
                    <span style="color:green">STATUS CODE 200</span>
                    """,
                    unsafe_allow_html=True
                    )
                    st.text(resp.headers)
                    st.write(
                        [i for i in content_json['Entities']]

                    )

            else:
                    st.markdown(
                    """
                    <span style="color:red">STATUS CODE 400</span>
                    """,
                    unsafe_allow_html=True
                    )
                

        # cb_name = st.checkbox("NAME", value=False)
        # cb_ssn = st.checkbox("SSN", value=False)
        # cb_address = st.checkbox("ADDRESS", value=False)
        # cb_phone = st.checkbox("PHONE", value=False)
        # cb_email = st.checkbox("EMAIL", value=False)
        # cb_pin = st.checkbox("PIN", value=False)
        # st.button("Submit")

        if st.button('Read Documentation'):

            st.write(
                f'<iframe src="http://localhost:8000/redoc", width=850, height=600  , scrolling=True></iframe>',
                unsafe_allow_html=True,
        )    
    elif choice == 'API-3':
        # for i in call_list.keys():
        #     fileInputMenu.append(i) 

        st.title("Masking And Anonymization")
        st.write("Please select the entities to be Masked/Anonymized")

        fileInputMenu = ["Select"]
        filename = st.selectbox("Company Name", fileInputMenu)

        company_name = 'HP Inc. (HPQ)'

        my_bucket = s3.Bucket("earnings-call-scraped")

        for object_summary in my_bucket.objects.filter(Prefix='entities/' + company_name):
            print('Found file %s' % object_summary.key)
            # print(read_file(object_summary.key))
            content_json = read_file_json(object_summary.key)

        available_entities = []
        for i in content_json['Entities']:
            available_entities.append(i['Type'])

        if 'DATE_TIME' in available_entities:
            cb_name = st.checkbox("DATE_TIME", value=False)
            if cb_name:
                date_time_rad = st.radio("",('Masking','Anonymization'))
                if date_time_rad == 'Anonymization': 
                    date_time_anon = st.radio("", ('Reversible', 'Permanent'))

        if 'NAME' in available_entities:
            cb_name = st.checkbox("NAME", value=False)
            if cb_name:
                name_rad = st.radio("",('Masking','Anonymization'))
                if name_rad == 'Anonymization':
                    name_anon = st.radio("", ('Reversible', 'Permanent'))
        if 'SSN' in available_entities:
            cb_ssn = st.checkbox("SSN", value=False)
            if cb_ssn:
                ssn_rad = st.radio("",('Masking','Anonymization'))
                if ssn_rad == 'Anonymization': 
                    ssn_anon = st.radio("", ('Reversible', 'Permanent'))
        if 'ADDRESS' in available_entities:
            cb_address = st.checkbox("ADDRESS", value=False)
            if cb_address:
                address_rad = st.radio("",('Masking','Anonymization'))
                if address_rad == 'Anonymization': 
                    address_anon = st.radio("", ('Reversible', 'Permanent'))

        if 'PHONE' in available_entities:
            cb_phone = st.checkbox("PHONE", value=False)
            if cb_phone:
                phone_rad = st.radio("",('Masking','Anonymization'))
                if phone_rad == 'Anonymization': 
                    phone_anon = st.radio("", ('Reversible', 'Permanent'))

        if 'EMAIL' in available_entities:
            cb_email = st.checkbox("EMAIL", value=False)
            if cb_email:
                email_rad = st.radio("",('Masking','Anonymization'))
                if email_rad == 'Anonymization': 
                    email_anon = st.radio("", ('Reversible', 'Permanent'))

        if 'PIN' in available_entities:
            cb_pin = st.checkbox("PIN", value=False)
            if cb_pin:
                pin_rad = st.radio("",('Masking','Anonymization'))
                if pin_rad == 'Anonymization': 
                    pin_anon = st.radio("", ('Reversible', 'Permanent'))

        bt_submit = st.button("Submit")
        if ((bt_submit) and (filename != "Select")) and ((cb_name == False) and #MAKE == later
            (cb_ssn== False) and (cb_address== False) and (cb_phone==False)
            and (cb_email==False) and (cb_pin==False)):

            st.error("Please select a Valid filename and at least one checkbox")

        elif ((bt_submit) and (filename != "Please select the file")) and ((cb_name == False) and
            (cb_ssn== False) and (cb_address== False) and (cb_phone==False)
            and (cb_email==False) and (cb_pin==False)):

            st.error("Please select at least one checkbox")

        elif ((bt_submit) and (filename == "Please select the file")) and ((cb_name == True) or
            (cb_ssn== True) or (cb_address== True) or (cb_phone==True)
            or (cb_email==True) or (cb_pin==True)):

            st.error("Please select a Valid filename")

        elif ((bt_submit) and (filename != "Please select the file")) and ((cb_name == True) or
            (cb_ssn== True) or (cb_address== True) or (cb_phone==True)
            or (cb_email==True) or (cb_pin==True)):
            st.write("process")

        # for button in available_entities:    


if __name__ == '__main__':
    main()