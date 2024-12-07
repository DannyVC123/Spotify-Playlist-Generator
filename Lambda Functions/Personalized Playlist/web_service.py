import boto3
import json

def lambda_handler(event, context):
    rekognition = boto3.client('rekognition')

    try:
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        
        s3_bucket = body['S3Bucket']
        s3_object = body['S3Object']

        s3 = boto3.resource('s3')
        s3_object = s3.Object(s3_bucket, s3_object)
        image = s3_object.get()['Body'].read()

        response = rekognition.detect_labels(Image={'Bytes': image}, MaxLabels=8)
        labels = [label['Name'] for label in response['Labels']]
        print("Labels found:")
        print(labels)

        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image Labels Detected Successfully',
                'data': json.dumps(labels)
            })
        }
        return response

    except Exception as e:
        return error_response(f"Error Recognizing Image Labels: {str(e)}")

def error_response(message):
    return {
        'statusCode': 500,
        'body': json.dumps({
            'message': message
        })
    }
