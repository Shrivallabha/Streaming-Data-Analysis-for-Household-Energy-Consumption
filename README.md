This repository contains a serverless architecture for streaming data analysis, that is robust and can be scaled to incoroprate a multitude of users by using concurrency in lambda functions. This project uses the AWS architecture, mainly - Amazon Kinesis, Amazon SageMaker and AWS Lambda functions.

Architecture Diagram

![](architecture_diagram.jpeg)

![](ElectricityConsumptionFlow.png)

Modelling:

For forecasting, we have taken a Multivariate Times Series forecasting approach to predict future usage of power by an individual household. For this, we utilized an LSTM to train on our dataset. 
After multiple training sessions, we have saved our model checkpoints on S3.

Model Deployment:
For real time inference, we have chosen Amazon Sagemaker to provide predictions on  real-time streaming data. Sagemaker offers an intriguing feature are allowing users to host multiple models on the same end point. 

In order to deploy our saved model, we are required to stored our models in compressed .tar.gz format.

The untarred model directory structure may look like this.
   model1
        |--[model_version_number]
            |--variables
            |--saved_model.pb
    model2
        |--[model_version_number]
            |--assets
            |--variables
            |--saved_model.pb

Creating a SageMaker Model
A SageMaker Model contains references to a model.tar.gz file in S3 containing serialized model data, and a Docker image used to serve predictions with that model.
You must package the contents in a model directory (including models, inference.py and external modules) in .tar.gz format in a file named "model.tar.gz" and upload it to S3. If you're on a Unix-based operating system, you can create a "model.tar.gz" using the tar utility:
tar -czvf model.tar.gz model
After uploading your model.tar.gz to an S3 URI, such as s3://your-bucket/your-models/model.tar.gz, create a SageMaker Model which will be used to generate inferences.
Creating an Endpoint
A SageMaker Endpoint hosts your TensorFlow Serving model for real-time inference. The InvokeEndpoint API is used to send data for predictions to your TensorFlow Serving model.

Using Python SDK:
predictor = tensorflow_serving_model.deploy(initial_instance_count=1,
                                            framework_version='1.12',
                                            instance_type='ml.p2.xlarge')
prediction = predictor.predict(data)

Using boto3 to invoke endpoint:

import boto3

client = boto3.client('sagemaker-runtime')

custom_attributes = "c000b4f9-df62-4c85-a0bf-7c525f9104a4"  # An example of a trace ID.
endpoint_name = "..."                                       # Your endpoint name.
content_type = "..."                                        # The MIME type of the input data in the request body.
accept = "..."                                              # The desired MIME type of the inference in the response.
payload = "..."                                             # Payload for inference.
response = client.invoke_endpoint(
    EndpointName=endpoint_name, 
    CustomAttributes=custom_attributes, 
    ContentType=content_type,
    Accept=accept,
    Body=payload
    )

print(response['CustomAttributes']) 



Deploying to Multi-Model Endpoint
Multi-Model Endpoint can be used together with Pre/Post-Processing. Each model will need its own inference.py otherwise default handlers will be used. An example of the directory structure of Multi-Model Endpoint and Pre/Post-Processing would look like this:
   /opt/ml/models/model1/model
        |--[model_version_number]
            |--variables
            |--saved_model.pb
    /opt/ml/models/model2/model
        |--[model_version_number]
            |--assets
            |--variables
            |--saved_model.pb


Feature 2: Monthly forecasting using Prophet

Considering real time streaming power usage data and the latest date we have collected the data for, we can forecast customers usage of power for the rest of the month. This can provide the customers with a lot of insight on whether to cut down on excessive usage of power.

Prophet uses Univariate Time Series forecasting and is trained on the entire dataset.
The checkpoint of the prophet model is saved in S3 storage.

m = Prophet()
m.fit(df)

The model is deployed for inference in such a way that given we have collected data till a certain time of the month, the model predicts the usage of power for the rest of the month.
We get this by feeding in a dataframe containing dates generated till the end of the month.

forecast = m.predict(dates_df)

Prophet also plots trends of usage, weekly, daily and yearly seasonality in the usage





