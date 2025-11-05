# aws-lambda-cloudformation-stacks

A collection of AWS Lambda functions with CloudFormation templates for deployment.

## Hello World S3 Reader

A simple Python Lambda function that demonstrates reading from an S3 bucket.

### Features

- Reads and lists objects from a specified S3 bucket
- Returns a "Hello World" message along with bucket information
- Handles errors gracefully
- Can be configured via event parameters or environment variables

### Files

- `lambda_function.py` - Main Lambda function code
- `cloudformation-template.yaml` - CloudFormation template for deployment
- `requirements.txt` - Python dependencies (boto3)

### Usage

#### Deploy with CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name hello-world-s3-stack \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=S3BucketName,ParameterValue=your-bucket-name \
  --capabilities CAPABILITY_IAM
```

#### Invoke the Lambda Function

```bash
aws lambda invoke \
  --function-name HelloWorldS3Reader \
  --payload '{"bucket_name": "your-bucket-name"}' \
  response.json
```

#### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the function locally
python lambda_function.py
```

### Function Input

The Lambda function accepts the following event structure:

```json
{
  "bucket_name": "your-s3-bucket-name"
}
```

If `bucket_name` is not provided in the event, the function will use the `S3_BUCKET_NAME` environment variable.

### Function Output

Success response:

```json
{
  "statusCode": 200,
  "body": {
    "message": "Hello World! Successfully read from S3 bucket: your-bucket-name",
    "bucket": "your-bucket-name",
    "object_count": 5,
    "objects": [
      {
        "key": "file1.txt",
        "size": 1024,
        "last_modified": "2024-01-01T12:00:00"
      }
    ],
    "hello": "world"
  }
}
```

Error response:

```json
{
  "statusCode": 400,
  "body": {
    "message": "Error: No bucket name provided",
    "hello": "world"
  }
}
```

### IAM Permissions

The Lambda function requires the following IAM permissions:

- `s3:ListBucket` - To list objects in the bucket
- `s3:GetObject` - To read objects from the bucket
- CloudWatch Logs permissions (provided by `AWSLambdaBasicExecutionRole`)

### Requirements

- Python 3.11 or later
- boto3 >= 1.26.0
- AWS account with appropriate permissions
- S3 bucket to read from

## License

This project is provided as-is for educational and demonstration purposes.