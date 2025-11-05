"""
Unit tests for the Hello World S3 Lambda function
"""
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the lambda function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lambda_function import lambda_handler


class TestLambdaFunction:
    """Test cases for lambda_handler function"""
    
    def test_missing_bucket_name(self):
        """Test that function returns error when no bucket name is provided"""
        event = {}
        context = {}
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'Error' in body['message']
        assert body['hello'] == 'world'
    
    @patch.dict(os.environ, {'S3_BUCKET_NAME': 'test-bucket-env'})
    def test_bucket_name_from_environment(self):
        """Test that function uses environment variable when event doesn't have bucket_name"""
        event = {}
        context = {}
        
        with patch('lambda_function.boto3.client') as mock_boto:
            mock_s3 = MagicMock()
            mock_boto.return_value = mock_s3
            mock_s3.list_objects_v2.return_value = {'Contents': []}
            
            result = lambda_handler(event, context)
            
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['bucket'] == 'test-bucket-env'
            assert body['hello'] == 'world'
    
    @patch('lambda_function.boto3.client')
    def test_successful_s3_read(self, mock_boto):
        """Test successful S3 bucket read with objects"""
        event = {'bucket_name': 'test-bucket'}
        context = {}
        
        # Mock S3 client and response
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        from datetime import datetime
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 1024,
                    'LastModified': datetime(2024, 1, 1, 12, 0, 0)
                },
                {
                    'Key': 'file2.txt',
                    'Size': 2048,
                    'LastModified': datetime(2024, 1, 2, 12, 0, 0)
                }
            ]
        }
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['bucket'] == 'test-bucket'
        assert body['object_count'] == 2
        assert len(body['objects']) == 2
        assert body['objects'][0]['key'] == 'file1.txt'
        assert body['objects'][0]['size'] == 1024
        assert body['hello'] == 'world'
        assert 'Successfully read from S3 bucket' in body['message']
    
    @patch('lambda_function.boto3.client')
    def test_empty_bucket(self, mock_boto):
        """Test S3 bucket with no objects"""
        event = {'bucket_name': 'empty-bucket'}
        context = {}
        
        # Mock S3 client with empty bucket
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {}  # No Contents key
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['bucket'] == 'empty-bucket'
        assert body['object_count'] == 0
        assert body['objects'] == []
        assert body['hello'] == 'world'
    
    @patch('lambda_function.boto3.client')
    def test_s3_client_error(self, mock_boto):
        """Test handling of S3 client errors"""
        event = {'bucket_name': 'test-bucket'}
        context = {}
        
        # Mock S3 client to raise ClientError
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {
                'Code': 'NoSuchBucket',
                'Message': 'The specified bucket does not exist'
            }
        }
        mock_s3.list_objects_v2.side_effect = ClientError(error_response, 'ListObjectsV2')
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Error reading from S3 bucket' in body['message']
        assert body['hello'] == 'world'
    
    @patch('lambda_function.boto3.client')
    def test_unexpected_error(self, mock_boto):
        """Test handling of unexpected errors"""
        event = {'bucket_name': 'test-bucket'}
        context = {}
        
        # Mock S3 client to raise unexpected exception
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.list_objects_v2.side_effect = Exception('Unexpected error')
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Unexpected error occurred' in body['message']
        assert body['hello'] == 'world'


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
