#!/bin/bash

# Set dummy AWS credentials
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy
export AWS_REGION=eu-west-1

export S3_BUCKET=bucket

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
localstack start

# Create an S3 bucket
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket $S3_BUCKET --create-bucket-configuration LocationConstraint=$AWS_REGION

# Dummy solution: waiting for timeout
sleep 35


# List all created resources
aws --endpoint-url=http://localhost:4566 s3 ls

echo "All resources created successfully."
