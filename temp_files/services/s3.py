import boto3
from botocore.exceptions import ClientError
from decouple import config
from fastapi import HTTPException


class S3Services:
    def __init__(self):
        self.key = config('AWS_ACCESS_KEY')
        self.secret = config('AWS_SECRET')
        self.s3 = boto3.client('s3', aws_access_key_id=self.key, aws_secret_access_key=self.secret)
        self.bucket = config('AWS_BUCKET')

    def upload_photo(self, path, key, ext):
        try:
            self.s3.upload_file(path, self.bucket, key, ExtraArgs={'ACL': 'public-read', 'ContentType': f'image/{ext}'})
            return f'https://{self.bucket}.s3.{config("AWS_REGION")}.amazonaws.com/{key}'
        except ClientError:
            raise HTTPException(status_code=500, detail='S3 is not available at the moment.')
        except Exception:
            raise HTTPException(status_code=500, detail='S3 is not available at the moment.')

    def delete_photo(self, key):
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except ClientError:
            raise HTTPException(status_code=500, detail='S3 is not available at the moment.')
        except Exception:
            raise HTTPException(status_code=500, detail='S3 is not available at the moment.')
