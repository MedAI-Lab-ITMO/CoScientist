"""Shared service clients (single process-wide instances)."""

from .clients.chemical_client import ChemServiceClient
from .config import get_settings
from .utils.s3_utils import S3BucketService

_settings = get_settings()

s3_service = S3BucketService(
    endpoint=_settings.s3_endpoint_url,
    access_key=_settings.s3_access_key,
    secret_key=_settings.s3_secret_key,
    bucket_name=_settings.s3_bucket_name,
)

chem_service = ChemServiceClient(
    host=_settings.chem_services_host,
    port=str(_settings.chem_services_port),
    timeout=_settings.chem_services_timeout,
)
