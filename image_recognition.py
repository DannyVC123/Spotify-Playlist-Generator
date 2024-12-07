# import datatier  # MySQL database access
# import awsutil  # helper functions for AWS
import boto3  # Amazon AWS

import json
import uuid
import pathlib
import logging
import sys
import os

from configparser import ConfigParser

class ImageRecognition:
    def __init__(self):
        config_file = 'playlist-config.ini'

        # gain access to our S3 bucket:
        s3_profile = 's3readwrite'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        boto3.setup_default_session(profile_name=s3_profile)

        configur = ConfigParser()
        configur.read(config_file)
        self.bucket_name = configur.get('s3', 'bucket_name')
        self.region_name = configur.get(s3_profile, 'region_name')

        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(self.bucket_name)
    
    def upload_image(self, image_name):
        if not os.path.exists(image_name):
            print("Local file '", image_name, "' does not exist...")
            return
        
        filename, extension = os.path.splitext(image_name)
        if extension.lower() not in ['.jpg', '.jpeg', '.png']:
            print('unsupported filetype')
        
        key_name = f'{filename}-{uuid.uuid4()}{extension}'
        self.bucket.upload_file(image_name, key_name, ExtraArgs={'ACL': 'public-read'})
        self.bucket.upload_file(image_name,
                                key_name,
                                ExtraArgs={
                                    'ACL': 'public-read',
                                    'ContentType': extension
                                })

        return key_name
    
    def detect_labels(self, key_name):
        client = boto3.client('rekognition', region_name=self.region_name)
        response = client.detect_labels(Image = 
                                        {
                                            'S3Object': {
                                                'Bucket': self.bucket_name,
                                                'Name': key_name
                                            }
                                        },
                                        MaxLabels=10)
        
        return json.dumps(response['Labels'])

'''
image_recognition = ImageRecognition()
# key_name = image_recognition.upload_image('pat.jpg')
labels = image_recognition.detect_labels('pumpkins.jpg')
print(labels)
'''

'''
# Read configuration
config_file = 'playlist-config.ini'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

# Load configuration
configur = ConfigParser()
configur.read(config_file)

# Get bucket details
bucket_name = configur.get('s3', 'bucket_name')
s3_profile = 's3readwrite'
region_name = configur.get(s3_profile, 'region_name')

print(f"Bucket Name: {bucket_name}")
print(f"Region: {region_name}")

# Try direct S3 and Rekognition clients
try:
    s3_client = boto3.client('s3', region_name=region_name)
    rekognition_client = boto3.client('rekognition', region_name=region_name)
    
    # List bucket contents
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    print("\nObjects in bucket:")
    for obj in response.get('Contents', []):
        print(obj['Key'])

except Exception as e:
    print("Error occurred:")
    print(f"Error type: {type(e)}")
    print(f"Error details: {str(e)}")
    
    import traceback
    traceback.print_exc()
'''
