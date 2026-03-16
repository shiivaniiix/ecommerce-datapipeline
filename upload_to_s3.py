from dotenv import load_dotenv
import boto3
import os

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

BUCKET = os.getenv("AWS_BUCKET_NAME")


def upload_to_s3():

    # upload customers file
    s3.upload_file(
        "data/customers.csv",
        BUCKET,
        "customers/customers.csv"
    )

    # upload orders file
    s3.upload_file(
        "data/orders.csv",
        BUCKET,
        "orders/orders.csv"
    )

    print("Files uploaded to S3")




'''
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def upload_orders_to_s3():

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )

    s3.upload_file(
        "data/orders.csv",
        os.getenv("AWS_BUCKET_NAME"),
        "orders/orders.csv"
    )

'''
'''
from dotenv import load_dotenv
import os

import boto3

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

bucket_name = "shivani-ecommerce-data-bucket"

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

s3.upload_file(
    "data/orders.csv",
    bucket_name,
    "orders/orders.csv"
)

print("File uploaded successfully")
'''