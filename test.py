import boto3
from decouple import config

s3 = boto3.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY'), aws_secret_access_key=config('AWS_SECRET'))


def upload_photo(path, key, ext):
    try:
        s3.upload_file(path, config('AWS_BUCKET'), key, ExtraArgs={'ACL': 'public-read', 'ContentType': f'image/{ext}'})
        # return f"https://{config('AWS_BUCKET')}.s3.{config('AWS_REGION')}.amazonaws.com/{key}"
    except Exception:
        raise Exception('S3 is not available at the moment.')


def delete_photo(key):
    try:
        response = s3.delete_object(Bucket=config('AWS_BUCKET'), Key=key)
        # return response['ResponseMetadata']['HTTPStatusCode']
        return response
    except Exception:
        raise Exception('S3 is not available at the moment.')


path = 'temp_files/Snakes-found-in-India.webp'
key = 'Snakes-found-in-India.webp'
ext = 'webp'

# upload_photo(path, key, ext)
rs = delete_photo(key)
print(rs)
