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
    print("Got Event")
    print(event)
    # parameter_object = event["queryStringParameters"]
    # user_id = parameter_object["id"]
    q = event["q"]
    print("Setting up Lex client")
    lex = boto3.client("lex-runtime")
    print("Obtaining Lex response")
    lex_response = lex.post_text(
        botName="PhotoKeywordBot",
        botAlias="PhotoKeywordBot",
        userId="123",
        inputText=q
    )
    print(lex_response)
    
    if "slots" not in lex_response:
        return {
            "statusCode": 200,
            "body": []
        }
    
    print("Obtaining slot values")
    slots = lex_response["slots"]
    slot_values = []
    for slot in slots.keys():
        if slots[slot] == None:
            break
        slot_values.append(slots[slot])
    
    print("Connecting to ElasticSearch")
    es_client = ElasticSearchClient(
        "search-pa-photos-tejbu3ru6einccfmr2l2wssmau.us-east-1.es.amazonaws.com",
        "us-east-1"
    )
    print("Connected to ElasticSearch")
    
    print(slot_values)
    photos = set()
    for label in slot_values:
        query = {
            "query": {
                "match": {
                    "labels": label
                }
            },
            "size": 10000
        }
        
        response = es_client.es.search(body=query, index="photos")
        print("Obtained Response")
        hits = response["hits"]["hits"]
        for hit in hits:
            photo_path = hit["_id"]
            photos.add(photo_path)
    
    print("Obtained Photos")
    print(photos)
    
    return {
        "statusCode": 200,
        "body": list(photos)
    }
        