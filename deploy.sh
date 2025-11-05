#!/bin/bash
# Manual deployment script for AWS Lambda
# This script can be used to deploy Lambda functions without GitHub Actions

set -e  # Exit on error

# Configuration
STACK_NAME="${1:-HelloWorldLambdaStack}"
FUNCTION_NAME="${2:-HelloWorldLambda}"
AWS_REGION="${3:-us-east-1}"
S3_BUCKET="lambda-deployments-$(whoami)"

echo "========================================"
echo "AWS Lambda Deployment Script"
echo "========================================"
echo "Stack Name: $STACK_NAME"
echo "Function Name: $FUNCTION_NAME"
echo "AWS Region: $AWS_REGION"
echo "S3 Bucket: $S3_BUCKET"
echo "========================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    echo "Please install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials are not configured"
    echo "Please run: aws configure"
    exit 1
fi

echo "✓ AWS credentials configured"

# Install dependencies if requirements.txt exists
if [ -f lambda/requirements.txt ]; then
    echo "Installing Python dependencies..."
    cd lambda
    pip install -r requirements.txt -t . --quiet
    cd ..
    echo "✓ Dependencies installed"
fi

# Package Lambda function
echo "Packaging Lambda function..."
cd lambda
zip -r ../lambda-deployment.zip . -x "*.pyc" -x "__pycache__/*" > /dev/null
cd ..
echo "✓ Lambda function packaged ($(du -h lambda-deployment.zip | cut -f1))"

# Create S3 bucket if it doesn't exist
echo "Checking S3 bucket..."
if aws s3api head-bucket --bucket "$S3_BUCKET" 2>/dev/null; then
    echo "✓ S3 bucket exists"
else
    echo "Creating S3 bucket..."
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket "$S3_BUCKET" --region "$AWS_REGION"
    else
        aws s3api create-bucket --bucket "$S3_BUCKET" --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi
    echo "✓ S3 bucket created"
fi

# Upload to S3
echo "Uploading Lambda package to S3..."
aws s3 cp lambda-deployment.zip s3://$S3_BUCKET/lambda-deployment.zip
echo "✓ Package uploaded to S3"

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" &> /dev/null; then
    echo "Updating existing stack..."
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://cloudformation/deploy-lambda.yaml \
        --parameters \
            ParameterKey=FunctionName,ParameterValue="$FUNCTION_NAME" \
            ParameterKey=S3Bucket,ParameterValue="$S3_BUCKET" \
            ParameterKey=S3Key,ParameterValue=lambda-deployment.zip \
        --capabilities CAPABILITY_NAMED_IAM || echo "No updates needed"

    echo "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" 2>/dev/null || true
else
    echo "Creating new stack..."
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://cloudformation/deploy-lambda.yaml \
        --parameters \
            ParameterKey=FunctionName,ParameterValue="$FUNCTION_NAME" \
            ParameterKey=S3Bucket,ParameterValue="$S3_BUCKET" \
            ParameterKey=S3Key,ParameterValue=lambda-deployment.zip \
        --capabilities CAPABILITY_NAMED_IAM

    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME"
fi

echo "✓ Stack deployed successfully"

# Get stack outputs
echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo "Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo "Test your Lambda function with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"name\":\"User\"}' response.json"
echo ""

# Cleanup
rm -f lambda-deployment.zip
echo "✓ Cleanup complete"
