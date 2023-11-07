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

    def upload_file(self, local_path, bucket_url, content_type):
        bucket = self.client.bucket(self.data_bucket)
        blob = bucket.blob(bucket_url)
        base64_content = base64.b64decode(local_path)
        blob.upload_from_string(base64_content, content_type=content_type)
        blob.make_public()
        return blob.public_url

    def upload_image(self, local_path, bucket_url):
        url = self.upload_file(local_path, bucket_url, content_type="image/png")
        return url
    
    def upload_tar(self, local_path, bucket_url):
        url = self.upload_file(local_path, bucket_url, content_type="application/x-tar")
        return url