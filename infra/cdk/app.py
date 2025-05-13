#!/usr/bin/env python3
from aws_cdk import App
from s3_stack import S3Stack
from opensearch_stack import OpenSearchStack
from lambda_stack import LambdaStack
from cognito_stack import CognitoStack

app = App()

s3_stack = S3Stack(app, "S3Stack")
opensearch_stack = OpenSearchStack(app, "OpenSearchStack")
lambda_stack = LambdaStack(app, "LambdaStack")
cognito_stack = CognitoStack(app, "CognitoStack")

app.synth()