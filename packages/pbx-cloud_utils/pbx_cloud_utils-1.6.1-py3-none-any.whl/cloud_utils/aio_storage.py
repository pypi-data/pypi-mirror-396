import datetime
import os
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Tuple

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobClient, ContainerClient
from google.cloud import storage as gcs_storage

from cloud_utils.const import GOOGLE_BUCKET_API_URL
from cloud_utils.types import (
    PbxACL,
    PbxStorageClass,
    S3AddressingStyles,
    UploadObjectData,
    azure_acl_map,
    azure_storage_class_map,
    gcs_acl_map,
    gcs_storage_class_map,
    s3_acl_map,
    s3_storage_class_map,
)
from cloud_utils.utils import get_account_key

try:
    from aiobotocore import config as s3_config
    from aiobotocore.session import get_session

    HAS_AIOBOTOCORE = True
except ImportError:  # pragma: no cover
    HAS_AIOBOTOCORE = False


class AsyncStorage(ABC):
    provider_storage_class_map: dict[str, str]
    provider_acl_map: dict[str, str]

    def __init__(self, bucket_name: str, region_name: str, **kwargs: Any):
        self.region_name: str = region_name
        self.bucket_name: str = bucket_name
        self.extra_kwargs: Any = kwargs

    @abstractmethod
    async def delete_object(self, key: str) -> None:
        pass

    @abstractmethod
    async def generate_presigned_url(
        self, key: str, size: str, content_md5: str, **kwargs: Any
    ) -> Tuple[str, dict]:
        pass

    @abstractmethod
    async def change_storage_class(
        self,
        key: str,
        target_storage_class: PbxStorageClass,
        acl: PbxACL = PbxACL.PUBLIC_READ,
    ) -> None:
        pass

    @abstractmethod
    async def copy(
        self, key: str, target_key: str, acl: PbxACL = PbxACL.AUTHENTICATED_READ
    ) -> None:
        pass

    @abstractmethod
    async def download(self, key: str) -> tuple[BytesIO, dict[str, str]]:
        pass

    @abstractmethod
    async def upload(
        self,
        key: str,
        content: BytesIO,
        mimetype: str,
        acl: PbxACL = PbxACL.PUBLIC_READ,
        target_storage_class: PbxStorageClass = PbxStorageClass.STANDARD,
    ) -> UploadObjectData:
        pass


class AsyncAmazonS3Storage(AsyncStorage):
    provider_storage_class_map: dict[str, str] = s3_storage_class_map
    provider_acl_map: dict[str, str] = s3_acl_map

    def __new__(cls, *args, **kwargs):
        if not HAS_AIOBOTOCORE:  # pragma: no cover
            raise ImportError("Required aiobotocore, please install aiobotocore>=1.4.0.")
        return super().__new__(cls)

    async def delete_object(self, key: str):
        session = get_session()
        async with session.create_client("s3", self.region_name) as client:
            await client.delete_object(Bucket=self.bucket_name, Key=key)

    async def generate_presigned_url(
        self,
        key: str,
        size: str,
        content_md5: str,
        addressing_style: S3AddressingStyles = "path",
        **kwargs: Any,
    ) -> Tuple[str, dict]:
        headers = {"Content-Length": str(size), "Content-MD5": content_md5}
        session = get_session()
        config = s3_config.AioConfig(s3={"addressing_style": addressing_style})
        async with session.create_client(
            "s3",
            region_name=self.region_name,
            config=config,
            **self.extra_kwargs,
        ) as client:
            url = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ContentLength": size,
                    "ContentMD5": content_md5,
                },
            )

            return url, headers

    async def change_storage_class(
        self,
        key: str,
        target_storage_class: PbxStorageClass,
        acl: PbxACL = PbxACL.PUBLIC_READ,
    ) -> None:
        session = get_session()
        async with session.create_client("s3", self.region_name, **self.extra_kwargs) as client:
            await client.copy_object(
                ACL=self.provider_acl_map[acl.name],
                Bucket=self.bucket_name,
                Key=key,
                CopySource={"Bucket": self.bucket_name, "Key": key},
                StorageClass=self.provider_storage_class_map[target_storage_class.name],
                MetadataDirective="COPY",
            )

    async def copy(
        self, key: str, target_key: str, acl: PbxACL = PbxACL.AUTHENTICATED_READ
    ) -> None:
        session = get_session()
        async with session.create_client("s3", self.region_name, **self.extra_kwargs) as client:
            await client.copy_object(
                ACL=self.provider_acl_map[acl.name],
                Bucket=self.bucket_name,
                Key=target_key,
                CopySource={"Bucket": self.bucket_name, "Key": key},
                MetadataDirective="COPY",
            )

    async def download(self, key: str) -> tuple[BytesIO, dict[str, str]]:
        session = get_session()
        async with session.create_client("s3", self.region_name, **self.extra_kwargs) as client:
            obj = await client.get_object(Bucket=self.bucket_name, Key=key)
            async with obj["Body"] as body_stream:
                data = await body_stream.read()
            return BytesIO(data), {
                "mimetype": obj.get("ContentType"),
                "storage_class": obj.get("StorageClass", "STANDARD"),
            }

    async def upload(
        self,
        key: str,
        content: BytesIO,
        mimetype: str,
        acl: PbxACL = PbxACL.PUBLIC_READ,
        target_storage_class: PbxStorageClass = PbxStorageClass.STANDARD,
    ) -> UploadObjectData:
        session = get_session()
        async with session.create_client("s3", self.region_name, **self.extra_kwargs) as client:
            response = await client.put_object(
                ACL=self.provider_acl_map[acl.name],
                Body=content.getvalue(),
                Bucket=self.bucket_name,
                Key=key,
                StorageClass=self.provider_storage_class_map[target_storage_class.name],
                ContentType=mimetype,
            )
            return UploadObjectData(md5sum=response["ETag"].replace('"', ""))


class AsyncAzureBlobStorage(AsyncStorage):
    provider_storage_class_map: dict[str, str] = azure_storage_class_map
    provider_acl_map: dict[str, str] = azure_acl_map

    def __init__(self, container_name: str, **kwargs: Any) -> None:
        connection_string = kwargs.get(
            "conn_str",
            os.environ.get("AZURE_STORAGE_CONNECTION_STRING", ""),
        )
        self.account_key: str = get_account_key(connection_string)
        self.container_name: str = container_name
        self.client: ContainerClient = ContainerClient.from_connection_string(
            conn_str=connection_string, container_name=container_name
        )

    @property
    def account_name(self) -> str:
        return self.client.account_name or ""

    async def delete_object(self, key: str):
        await self.client.delete_blob(key)

    async def generate_presigned_url(
        self, key: str, size: str, content_md5: str, **kwargs: Any
    ) -> Tuple[str, dict]:
        headers = {
            "x-ms-version": "2021-04-10",
            "x-ms-blob-type": "BlockBlob",
        }
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=key,
            account_key=self.account_key,
            permission=BlobSasPermissions(create=True, write=True),
            expiry=datetime.datetime.now() + datetime.timedelta(hours=kwargs.get("expiry", 1)),
        )
        container_blob_url = self.client.get_blob_client(key).url
        blob_client = BlobClient.from_blob_url(container_blob_url, credential=sas_token)

        return blob_client.url, headers

    async def change_storage_class(
        self, key: str, target_storage_class: PbxStorageClass, acl: PbxACL = PbxACL.PUBLIC_READ
    ) -> None:
        raise NotImplementedError()

    async def copy(
        self, key: str, target_key: str, acl: PbxACL = PbxACL.AUTHENTICATED_READ
    ) -> None:
        raise NotImplementedError()

    async def download(self, key: str) -> tuple[BytesIO, dict[str, str]]:
        raise NotImplementedError()

    async def upload(
        self,
        key: str,
        content: BytesIO,
        mimetype: str,
        acl: PbxACL = PbxACL.PUBLIC_READ,
        target_storage_class: PbxStorageClass = PbxStorageClass.STANDARD,
    ) -> UploadObjectData:
        raise NotImplementedError()


class HybridAsyncGoogleCloudStorage(AsyncStorage):
    provider_storage_class_map: dict[str, str] = gcs_storage_class_map
    provider_acl_map: dict[str, str] = gcs_acl_map
    bucket_client: gcs_storage.Bucket
    endpoint_url: str

    def __init__(self, endpoint_url: str = "", gcs_project_id: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gcs_project = gcs_project_id or os.environ.get("GCS_PROJECT_ID")
        gcs_storage_client_kwargs = {
            key.removeprefix("gcs_"): value
            for key, value in kwargs.items()
            if key.startswith("gcs_")
        }
        client = gcs_storage.Client(project=self.gcs_project, **gcs_storage_client_kwargs)
        bucket = client.bucket(self.bucket_name)
        self.bucket_client = bucket
        self.endpoint_url = endpoint_url or GOOGLE_BUCKET_API_URL

    async def delete_object(self, key: str) -> None:
        raise NotImplementedError()

    async def generate_presigned_url(
        self, key: str, size: str, content_md5: str, **kwargs: Any
    ) -> Tuple[str, dict]:
        raise NotImplementedError()

    async def change_storage_class(
        self,
        key: str,
        target_storage_class: PbxStorageClass,
        acl: PbxACL = PbxACL.PUBLIC_READ,
    ) -> None:
        # TODO use async API
        self.bucket_client.blob(key).update_storage_class(
            self.provider_storage_class_map[target_storage_class.name]
        )

    async def copy(
        self, key: str, target_key: str, acl: PbxACL = PbxACL.AUTHENTICATED_READ
    ) -> None:
        session = get_session()
        async with session.create_client(
            "s3", self.region_name, endpoint_url=self.endpoint_url
        ) as client:
            await client.copy_object(
                ACL=self.provider_acl_map[acl.name],
                Bucket=self.bucket_name,
                Key=target_key,
                CopySource={"Bucket": self.bucket_name, "Key": key},
                MetadataDirective="COPY",
            )

    async def download(self, key: str) -> tuple[BytesIO, dict[str, str]]:
        session = get_session()
        async with session.create_client(
            "s3", self.region_name, endpoint_url=self.endpoint_url
        ) as client:
            obj = await client.get_object(Bucket=self.bucket_name, Key=key)
            async with obj["Body"] as body_stream:
                data = await body_stream.read()
            storage_class = obj["ResponseMetadata"]["HTTPHeaders"]["x-goog-storage-class"]
            return BytesIO(data), {
                "mimetype": obj.get("ContentType"),
                "storage_class": storage_class,
            }

    async def upload(
        self,
        key: str,
        content: BytesIO,
        mimetype: str,
        acl: PbxACL = PbxACL.PUBLIC_READ,
        target_storage_class: PbxStorageClass = PbxStorageClass.STANDARD,
    ) -> UploadObjectData:
        session = get_session()
        async with session.create_client(
            "s3", self.region_name, endpoint_url=self.endpoint_url
        ) as client:
            response = await client.put_object(
                ACL=self.provider_acl_map[acl.name],
                Body=content.getvalue(),
                Bucket=self.bucket_name,
                Key=key,
                StorageClass=self.provider_storage_class_map[target_storage_class.name],
                ContentType=mimetype,
            )
            return UploadObjectData(md5sum=response["ETag"].replace('"', ""))
