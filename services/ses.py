from decouple import config
import boto3


class SESServices:
    def __init__(self):
        secret_key_id = config('AWS_ACCESS_KEY')
        secret_key_access = config('AWS_SECRET')
        self.ses = boto3.client(
            'ses', region_name=config('SES_REGION'),
            aws_access_key_id=secret_key_id,
            aws_secret_access_key=secret_key_access
        )

    def send_email(self, subject, to_addresses, text_data):
        body = {}
        body.update({'Text': {'Data': text_data, 'Charset': 'UTF-8'}})
        try:
            self.ses.send_email(
                Source=config('SES_SOURCE_EMAIL'),
                Destination={
                    'ToAddresses': to_addresses,
                    'CcAddresses': [],
                    'BccAddresses': []
                },
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body
                }
            )
        except Exception as ex:
            raise ex
