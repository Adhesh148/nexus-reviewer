# Nexus GitHub PR Bot

The Nexus GitHub PR Bot is an automated review system designed to generate review comments for pull requests (PRs) using AI. The bot leverages LangGraph and OpenAI to process PR events, analyze file changes, and provide actionable review feedback.

## Overview

Whenever a pull request is opened, the bot is triggered via a webhook, which calls an API Gateway endpoint integrated with an AWS Lambda function. The Lambda function uses LangGraph to execute a workflow that retrieves PR files, generates review comments, and updates the PR with these comments.

## Project Structure

- **src**: Contains the code for handling Lambda function execution.
- **config**: Configuration settings for the Lambda function.
- **workflow**: Contains LangGraph workflows for processing PRs.

## Lambda Deployment Guide

This guide explains how to deploy your Lambda function using AWS Lambda. Follow the steps below to prepare and upload your deployment package.

### Prerequisites

- AWS CLI installed and configured
- An S3 bucket to store the deployment package
- AWS Lambda function configured to use the S3 bucket

### Steps to Deploy to Lambda

#### 1. Prepare the Deployment Package

1. Create a `package` directory:

    ```bash
    mkdir package
    ```

2. Install dependencies into the `package` directory:

    ```bash
    pip install -r requirements.txt --platform manylinux2014_x86_64 --target ./package/ --only-binary=:all: --python-version 3.11 --no-cache-dir
    ```

3. Zip the contents of the `package` directory:

    ```bash
    cd package
    zip -r ../my_deployment_package.zip .
    ```

4. Zip the contents of the `src` directory (containing your Lambda function code):

    ```bash
    cd ../src
    zip -r ../my_deployment_package.zip .
    ```

#### 2. Upload to S3 Bucket

1. Upload the deployment package to your S3 bucket. Replace `<bucket-name>` with your S3 bucket name and `<path-to-zip>` with the path to the zip file:

    ```bash
    aws s3 cp ../my_deployment_package.zip s3://<bucket-name>/<path-to-zip>
    ```

#### 3. Update Lambda Function Code

1. Open the AWS Lambda console or use the AWS CLI to update your Lambda function code to use the newly uploaded deployment package.

2. To update using the AWS CLI, replace `<function-name>`, `<bucket-name>`, and `<path-to-zip>` with your Lambda function name, S3 bucket name, and the path to the zip file, respectively:

    ```bash
    aws lambda update-function-code --function-name <function-name> --s3-bucket <bucket-name> --s3-key <path-to-zip>
    ```

### Additional Notes

- Ensure your Lambda function has the appropriate IAM roles and permissions to access the S3 bucket.
- Verify that the deployment package is properly structured and includes all necessary dependencies.

### Troubleshooting

- If you encounter issues with the deployment, check the Lambda function logs in CloudWatch for any errors.
- Verify that all required dependencies are included in the `requirements.txt` and are installed correctly.

For more detailed information, refer to the [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html).