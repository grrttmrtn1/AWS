import requests
import boto3
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    security_group_id = ''
    homeIP = ""
    cloudflareUri = "https://www.cloudflare.com/ips-v4"
    sgIPs = []
    r = requests.get(cloudflareUri)
    cloudflareIPs = str(r.content).replace('b','').replace("'","").rstrip('\\n').split('\\n')
    #print(cloudflareIPs)
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_security_groups(GroupIds=[security_group_id])
        for rule in response['SecurityGroups'][0]['IpPermissions']:
            if (rule['ToPort']) == 443:
                for range in rule['IpRanges']:
                    #print(range['CidrIp'])
                    if range['CidrIp'].strip() != homeIP:
                        if range['CidrIp'] in cloudflareIPs:
                            sgIPs.append(range['CidrIp'])
                        else:
                            print("Remove " + range['CidrIp'])
                            ec2.revoke_security_group_ingress(
                                GroupId=security_group_id,
                                IpPermissions=[
                                    {'IpProtocol': 'tcp',
                                     'FromPort': 443,
                                     'ToPort': 443,
                                     'IpRanges': [{'CidrIp': range['CidrIp']}]}
                                ])
                for ip in cloudflareIPs:
                    if ip not in sgIPs and range['CidrIp'] != homeIP:
                        print(ip)
                        data = ec2.authorize_security_group_ingress(
                                GroupId=security_group_id,
                                IpPermissions=[
                                    {'IpProtocol': 'tcp',
                                     'FromPort': 443,
                                     'ToPort': 443,
                                     'IpRanges': [{'CidrIp': ip}]}
                                ])
    except ClientError as e:
        print(e)
    
    


