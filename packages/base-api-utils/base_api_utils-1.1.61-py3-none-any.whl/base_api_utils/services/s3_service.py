import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .abstract_storage_service import AbstractStorageService
from ..utils.exceptions import S3Exception
from ..utils.config import config


class S3Service(AbstractStorageService):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=config("STORAGE.ENDPOINT_URL"),
            aws_access_key_id=config("STORAGE.ACCESS_KEY_ID"),
            aws_secret_access_key=config("STORAGE.SECRET_ACCESS_KEY"),
            region_name=config("STORAGE.REGION_NAME")
        )

    def get_file_metadata(self, source_file_path:str, bucket: str =config("STORAGE.SOURCE.BUCKET_NAME")) -> dict:
        try:
            head =  self.s3_client.head_object(Bucket=bucket, Key=source_file_path)
            return head.get("Metadata", {})
        except (BotoCoreError, ClientError) as e:
            raise S3Exception("Cannot get file metadata.")

    def copy_file(self, source_file_path, target_file_path):
        try:
            copy_source = {
                'Bucket': config("STORAGE.SOURCE.BUCKET_NAME"),
                'Key': source_file_path
            }
            self.s3_client.copy(
                copy_source,
                config("STORAGE.TARGET.BUCKET_NAME"),
                target_file_path
            )
            self.s3_client.put_object_acl(
                Bucket=config("STORAGE.TARGET.BUCKET_NAME"),
                Key=target_file_path,
                ACL='public-read'
            )
        except (BotoCoreError, ClientError) as e:
            logging.getLogger('api').error(e)
            raise S3Exception(f'Cannot copy {source_file_path} to {target_file_path}')


    def delete_file(self, file_path):
        try:
            self.s3_client.delete_object(
                Bucket=config("STORAGE.TARGET.BUCKET_NAME"),
                Key=file_path
            )
        except (BotoCoreError, ClientError) as e:
            logging.getLogger('api').error(e)
            raise S3Exception(f'Cannot delete {file_path} from storage')
