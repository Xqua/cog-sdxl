import base64
import json
import logging
import os
from google.cloud import storage
from google.oauth2 import service_account

class BucketConnector:
    def __init__(self) -> None:
        service_account_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info)
        self.client = storage.Client(credentials=credentials)
        self.data_bucket = os.environ["DATA_BUCKET"]
    
    def download_file(self, bucket_url, local_path):
        logging.info(f"Downloading file {bucket_url} to {local_path}...")
        bucket = self.client.bucket(self.data_bucket)
        blob = bucket.blob(bucket_url)
        blob.download_to_filename(local_path)

    def upload_file(self, local_path, bucket_url, content_type=None):
        bucket = self.client.bucket(self.data_bucket)
        blob = bucket.blob(bucket_url)
        blob.upload_from_filename(local_path, content_type=content_type)
        blob.make_public()
        return blob.public_url

    def upload_image(self, local_path, bucket_url):
        url = self.upload_file(local_path, bucket_url, content_type="image/png")
        return url
    
    def upload_tar(self, local_path, bucket_url):
        url = self.upload_file(local_path, bucket_url, content_type="application/x-tar")
        return url