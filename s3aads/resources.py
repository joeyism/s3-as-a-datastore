import boto3
from botocore.config import Config

config = Config(s3={"use_accelerate_endpoint": False})
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3', config=config)
