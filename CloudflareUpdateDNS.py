import boto3
from botocore.exceptions import ClientError
import requests
import os
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instanceID = os.environ['instanceid']
    cloudflareAPIKey = os.environ['apikey']
    dnsZone = os.environ['dnszone']
    authEmail = os.environ['authemail']
    zoneId = os.environ['zoneid']
    record = os.environ['dnsrecord']
    recordId = os.environ['recordid']
    try:
        response = ec2.describe_network_interfaces(
                    Filters=[
                    {
                        'Name': 'attachment.instance-id',
                        'Values': [
                        instanceID
                        ]
                    }])
        publicIP = response['NetworkInterfaces'][0]['Association']['PublicIp']
        print(publicIP)
        data = {'type':'A','name':record,'content':publicIP,'ttl':120,'proxied': True}
        data = json.dumps(data)
        cloudflareURI = 'https://api.cloudflare.com/client/v4/zones/' + zoneId + '/dns_records/' + recordId
        headers = {'X-Auth-Email': authEmail, 'X-Auth-Key': cloudflareAPIKey,'Content-Type': 'application/json'}
        #headers = json.dumps(headers)
        try:
            r = requests.put(cloudflareURI, headers=headers, data=data)
            print(r.content)
        except:
            print('Status Code: ' + r.status_code + '\n' + 'Error: ' + r.content)
    except ClientError as e:
        print(e)
    
    
    

