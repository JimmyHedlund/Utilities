from md_converter_shared.storage import StorageConfig, StorageService as SharedStorageService

from app.core.config import get_settings


class StorageService(SharedStorageService):
    def __init__(self, public_urls: bool = False) -> None:
        settings = get_settings()
        super().__init__(
            StorageConfig(
                endpoint_url=settings.s3_endpoint_url,
                public_endpoint_url=settings.s3_public_endpoint_url,
                uploads_bucket=settings.s3_bucket_uploads,
                outputs_bucket=settings.s3_bucket_outputs,
                access_key_id=settings.s3_access_key_id,
                secret_access_key=settings.s3_secret_access_key,
                signed_url_ttl_seconds=settings.signed_url_ttl_seconds,
            ),
            public_urls=public_urls,
        )
