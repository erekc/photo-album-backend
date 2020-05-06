import boto3
import requests
import json
import random
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

class ElasticSearchClient:
    
    def __init__(self, host, region):
        self.host = host # For example, my-test-domain.us-east-1.es.amazonaws.com
        self.region = region # e.g. us-west-1
        self.service = 'es'
        self.credentials = boto3.Session().get_credentials()
        self.awsauth = AWS4Auth(self.credentials.access_key, self.credentials.secret_key,\
            self.region, self.service, session_token=self.credentials.token)
        self.es = Elasticsearch(
            hosts = [{'host': self.host, 'port': 443}],
            http_auth = self.awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
        )

def lambda_handler(event, context):
    # TODO implement
    put_event = event["Records"][0]
    photo = put_event["s3"]["object"]["key"]
    print(photo)
    image = {
        "S3Object": {
            "Bucket": "pa-b2",
            "Name": photo
        }
    }
    
    print(image)
    rekognition = boto3.client("rekognition")
    label_detection = rekognition.detect_labels(Image=image)
    print(label_detection)
    labels = []
    for label_object in label_detection["Labels"]:
        label = label_object["Name"]
        labels.append(label)
    print(labels)
    
    es_photo_object = {
        "objectkey": photo,
        "bucket": "pa-b2",
        "cretedTimestamp": str(time.time()),
        "labels": labels
    }
    
    es_client = ElasticSearchClient(
        "search-pa-photos-tejbu3ru6einccfmr2l2wssmau.us-east-1.es.amazonaws.com",
        "us-east-1"
    )
    
    response = es_client.es.index(index="photos", id=es_photo_object["objectkey"], body=es_photo_object)
    print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }