# AWS Lambda CloudFormation CI/CD Pipeline

This repository provides a complete CI/CD pipeline for deploying AWS Lambda functions using CloudFormation templates and GitHub Actions. It includes templates to create, update, and delete Lambda functions, along with a simple Hello World Python Lambda function.

## 🚀 Features

- **Automated CI/CD Pipeline**: GitHub Actions workflow for continuous deployment
- **CloudFormation Templates**: Infrastructure as Code for Lambda functions
- **Create Lambda Functions**: Template to create new Lambda functions with IAM roles
- **Deploy Lambda Functions**: Template to deploy code from S3 to existing functions
- **Delete Lambda Functions**: Template and automation to clean up resources
- **Hello World Example**: Simple Python Lambda function to get started

## 📋 Prerequisites

Before using this repository, you need:

1. **AWS Account**: An active AWS account with appropriate permissions
2. **GitHub Secrets**: Configure the following secrets in your repository:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key ID
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
3. **AWS Permissions**: The AWS credentials should have permissions for:
   - Lambda (create, update, delete functions)
   - IAM (create and manage roles)
   - CloudFormation (create, update, delete stacks)
   - S3 (create buckets, upload objects)
   - CloudWatch Logs (create log groups)

## 🏗️ Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-lambda.yml       # GitHub Actions CI/CD workflow
├── cloudformation/
│   ├── create-lambda.yaml          # Template to create new Lambda function
│   ├── deploy-lambda.yaml          # Template to deploy Lambda code from S3
│   └── delete-lambda.yaml          # Template to delete Lambda resources
├── lambda/
│   ├── lambda_function.py          # Hello World Python Lambda function
│   └── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

## 🔧 Setup Instructions

### Step 1: Configure AWS Credentials in GitHub

1. Go to your GitHub repository settings
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### Step 2: Customize Configuration

Edit the `.github/workflows/deploy-lambda.yml` file to customize:

```yaml
env:
  AWS_REGION: us-east-1              # Change to your preferred region
  LAMBDA_FUNCTION_NAME: HelloWorldLambda
  S3_BUCKET: lambda-deployments-${{ github.repository_owner }}
```

## 📦 CloudFormation Templates

### 1. Create Lambda Function (`create-lambda.yaml`)

Creates a new Lambda function with:
- Lambda function with configurable runtime, memory, and timeout
- IAM execution role with basic Lambda permissions
- CloudWatch log group for function logs

**Usage:**
```bash
aws cloudformation create-stack \
  --stack-name MyLambdaStack \
  --template-body file://cloudformation/create-lambda.yaml \
  --parameters \
    ParameterKey=FunctionName,ParameterValue=MyFunction \
    ParameterKey=Runtime,ParameterValue=python3.11 \
  --capabilities CAPABILITY_NAMED_IAM
```

### 2. Deploy Lambda Function (`deploy-lambda.yaml`)

Deploys Lambda function code from S3:
- Updates Lambda function with code from S3
- Creates/updates IAM role with S3 access
- Tracks deployments with Lambda versions

**Usage:**
```bash
aws cloudformation create-stack \
  --stack-name MyDeploymentStack \
  --template-body file://cloudformation/deploy-lambda.yaml \
  --parameters \
    ParameterKey=FunctionName,ParameterValue=HelloWorldLambda \
    ParameterKey=S3Bucket,ParameterValue=my-bucket \
    ParameterKey=S3Key,ParameterValue=lambda-deployment.zip \
  --capabilities CAPABILITY_NAMED_IAM
```

### 3. Delete Lambda Function (`delete-lambda.yaml`)

Cleans up Lambda resources:
- Deletes Lambda function
- Removes IAM roles
- Optionally deletes CloudWatch log groups

**Usage:**
```bash
aws cloudformation create-stack \
  --stack-name CleanupStack \
  --template-body file://cloudformation/delete-lambda.yaml \
  --parameters \
    ParameterKey=FunctionName,ParameterValue=MyFunction \
  --capabilities CAPABILITY_NAMED_IAM
```

## 🚦 CI/CD Workflow

The GitHub Actions workflow automatically:

1. **On Push to Main Branch**:
   - Installs Python dependencies
   - Packages Lambda function into ZIP file
   - Uploads package to S3
   - Deploys/updates CloudFormation stack
   - Displays deployment outputs

2. **Manual Workflow Dispatch**:
   - Choose action: deploy, update, or delete
   - Specify custom stack name
   - Execute selected operation

### Triggering Deployment

**Automatic Deployment:**
```bash
# Make changes to Lambda function
git add lambda/lambda_function.py
git commit -m "Update Lambda function"
git push origin main
```

**Manual Deployment:**
1. Go to **Actions** tab in GitHub
2. Select "Deploy Lambda to AWS" workflow
3. Click "Run workflow"
4. Choose action and stack name
5. Click "Run workflow"

## 🐍 Hello World Lambda Function

The included `lambda/lambda_function.py` demonstrates:
- Proper Lambda handler signature
- Event processing
- JSON response formatting
- Logging best practices
- Local testing capability

**Test Locally:**
```bash
cd lambda
python lambda_function.py
```

**Test in AWS:**
```bash
aws lambda invoke \
  --function-name HelloWorldLambda \
  --payload '{"name": "GitHub User"}' \
  response.json
cat response.json
```

## 🔄 Updating Lambda Code

1. **Modify your Lambda function**:
   ```bash
   vim lambda/lambda_function.py
   ```

2. **Commit and push changes**:
   ```bash
   git add lambda/
   git commit -m "Update Lambda function"
   git push origin main
   ```

3. **GitHub Actions will automatically**:
   - Package your code
   - Upload to S3
   - Update the Lambda function

## 🗑️ Deleting Resources

### Delete via GitHub Actions:
1. Go to **Actions** > **Deploy Lambda to AWS**
2. Click "Run workflow"
3. Select action: **delete**
4. Enter stack name
5. Run workflow

### Delete via AWS CLI:
```bash
# Delete the stack
aws cloudformation delete-stack --stack-name HelloWorldLambdaStack

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name HelloWorldLambdaStack
```

## 🛠️ Advanced Usage

### Adding Dependencies

Add Python packages to `lambda/requirements.txt`:
```
requests==2.31.0
boto3>=1.28.0
```

### Multiple Lambda Functions

Create separate directories for each function:
```
lambda/
├── function1/
│   ├── lambda_function.py
│   └── requirements.txt
├── function2/
│   ├── lambda_function.py
│   └── requirements.txt
```

Update the workflow to deploy multiple functions.

### Environment Variables

Add environment variables in CloudFormation template:
```yaml
Environment:
  Variables:
    ENV: production
    API_KEY: !Ref ApiKeyParameter
```

## 📊 Monitoring

### View Logs:
```bash
aws logs tail /aws/lambda/HelloWorldLambda --follow
```

### Check Function Metrics:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=HelloWorldLambda \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## 🔒 Security Best Practices

1. **Use IAM Roles**: Never hardcode credentials in code
2. **Principle of Least Privilege**: Grant minimum required permissions
3. **Secrets Management**: Use AWS Secrets Manager or Parameter Store
4. **Enable Encryption**: Encrypt environment variables and S3 objects
5. **VPC Configuration**: Deploy Lambda in VPC for sensitive operations
6. **Regular Updates**: Keep dependencies and runtime updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Issue: Stack creation fails
- Check AWS credentials are valid
- Verify IAM permissions
- Check CloudFormation events for errors

### Issue: Lambda function not updating
- Verify S3 bucket exists and is accessible
- Check GitHub Actions logs
- Ensure CloudFormation stack exists

### Issue: GitHub Actions workflow fails
- Verify GitHub secrets are set correctly
- Check AWS service limits
- Review workflow logs in Actions tab

## 📚 Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/)