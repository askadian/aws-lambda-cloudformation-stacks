"""
Hello World Lambda function that reads from an S3 bucket.

This AWS Lambda function demonstrates basic S3 operations by listing
objects in a specified S3 bucket.
"""

import json
import os
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    """
    AWS Lambda handler function that reads from an S3 bucket.
    
    Args:
        event: Lambda event object (can contain bucket_name parameter)
        context: Lambda context object
        
    Returns:
        dict: Response containing status code and message
    """
    print("Hello World! Starting S3 bucket read operation...")
    
    # Get bucket name from event or environment variable
    bucket_name = event.get('bucket_name') or os.environ.get('S3_BUCKET_NAME')
    
    if not bucket_name:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error: No bucket name provided. Please specify bucket_name in event or S3_BUCKET_NAME environment variable.',
                'hello': 'world'
            })
        }
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # List objects in the bucket
        print(f"Reading from S3 bucket: {bucket_name}")
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=10  # Limit to first 10 objects for demo
        )
        
        # Extract object information
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        message = f"Hello World! Successfully read from S3 bucket: {bucket_name}"
        print(message)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'bucket': bucket_name,
                'object_count': len(objects),
                'objects': objects,
                'hello': 'world'
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"Error reading from S3 bucket: {error_code} - {error_message}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error reading from S3 bucket: {error_code}',
                'error': error_message,
                'hello': 'world'
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unexpected error occurred',
                'error': str(e),
                'hello': 'world'
            })
        }


if __name__ == "__main__":
    # For local testing
    test_event = {
        'bucket_name': 'my-test-bucket'
    }
    test_context = {}
    
    result = lambda_handler(test_event, test_context)
    print("\n--- Test Result ---")
    print(json.dumps(result, indent=2))
