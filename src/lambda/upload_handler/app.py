import boto3
from typing import Dict, Any
from aws_lambda_typing.context import Context as LambdaContext

def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    return {
        "statusCode": 200,
        "boto3_version": boto3.__version__
    }