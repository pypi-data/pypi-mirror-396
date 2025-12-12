# flake8: noqa A005
from dataclasses import dataclass
from enum import IntEnum
from typing import Literal

S3AddressingStyles = Literal["path", "virtual", "auto"]


class PbxStorageClass(IntEnum):
    STANDARD = 0
    INFREQUENT_ACCESS = 1
    ARCHIVE = 2


s3_storage_class_map: dict[str, str] = {
    PbxStorageClass.STANDARD.name: "STANDARD",
    PbxStorageClass.INFREQUENT_ACCESS.name: "ONEZONE_IA",
    PbxStorageClass.ARCHIVE.name: "GLACIER",
}

azure_storage_class_map: dict[str, str] = {
    PbxStorageClass.STANDARD.name: "Hot",
    PbxStorageClass.INFREQUENT_ACCESS.name: "Cool",
    PbxStorageClass.ARCHIVE.name: "Archive",
}

gcs_storage_class_map: dict[str, str] = {
    PbxStorageClass.STANDARD.name: "STANDARD",
    PbxStorageClass.INFREQUENT_ACCESS.name: "NEARLINE",
    PbxStorageClass.ARCHIVE.name: "ARCHIVE",
}


class PbxACL(IntEnum):
    PUBLIC_READ = 0
    AUTHENTICATED_READ = 1


s3_acl_map: dict[str, str] = {
    PbxACL.PUBLIC_READ.name: "public-read",
    PbxACL.AUTHENTICATED_READ.name: "authenticated-read",
}

azure_acl_map: dict[str, str] = {
    PbxACL.PUBLIC_READ.name: "public-read",
    PbxACL.AUTHENTICATED_READ.name: "authenticated-read",
}

gcs_acl_map: dict[str, str] = {
    PbxACL.PUBLIC_READ.name: "public-read",
    PbxACL.AUTHENTICATED_READ.name: "project-private",
}


@dataclass
class UploadObjectData:
    md5sum: str
