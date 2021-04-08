import json
import boto3
import time
#from botocore.vendored import requests
import requests
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # TODO implement
    print(event)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        photo = record['s3']['object']['key']

        metadata = getS3Metadata(bucket,photo)
        print(metadata)

        #get labels of uploaded pic
        labels = []
        labels = get_photo_labels(bucket, photo)
        print(labels)

        if bool(metadata):
            print("<---------Entered if statement------------>")
            metadataList = metadata['customlabels'].split(',')
            labels = labels + metadataList
            print (labels)

        #create a json object of the labels detected by Rekognition
        new_doc = {"objectKey": photo,
                    "bucket": bucket,
                    "createdTimestamp": time.strftime("%Y%m%d-%H%M%S"),
                    "labels": labels
                   }
        print(bucket, photo, labels)
        print (new_doc)

        #add index to photo
        index_into_es('photos','photo',json.dumps(new_doc))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda LF1 index-!')
    }

def get_photo_labels(bucket,photo):

    rekClient = boto3.client('rekognition')

    response = rekClient.detect_labels(Image={'S3Object': {'Bucket': bucket,'Name': photo}}, MaxLabels=10, MinConfidence=90)
    #print(response)
    #print(response['Labels'])
    labels = [label['Name'] for label in response['Labels']]
    print(labels)
    return labels

def index_into_es(index, type_doc, new_doc):
    region = 'us-west-2' # e.g. us-west-1
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    endpoint = 'https://search-photos-gbk7gmd24z2gaphfyeqb4wylcm.us-west-2.es.amazonaws.com/{}/{}'.format(index, type_doc)
    headers = {'Content-Type':'application/json'}
    #res = requests.post(endpoint, data=new_doc, headers=headers)
    #res = requests.get('https://search-photos-gbk7gmd24z2gaphfyeqb4wylcm.us-west-2.es.amazonaws.com')
    print("<----Make Call------->")
    res = requests.post(endpoint,  auth=awsauth, data=new_doc, headers=headers)
    print("<----Response------->")
    print(res.content)


def getS3Metadata(bucket, photo):
    region = 'us-west-2'
    credentials = boto3.Session().get_credentials()
    YOUR_ACCESS_KEY = "AKIARW332D32CJCM5OEU"
    YOUR_SECRET_KEY = "Pca3RowIg7iNDsVSD1hdMKmNi/wqwaW+Ma7fCcdT"

    client = boto3.client('s3', region_name=region,
                        aws_access_key_id= YOUR_ACCESS_KEY,
                        aws_secret_access_key= YOUR_SECRET_KEY)

    response = client.head_object(
        Bucket = bucket,
        Key = photo
        )

    print(response)

    return response['Metadata']