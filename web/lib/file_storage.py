from datetime import datetime, timedelta
from django.conf import settings
import os
from shutil import copyfileobj
from azure.storage.blob import BlockBlobService, BlobPermissions

from lib import site

def save_file_obj(dest_path, file_obj, container):
    if settings.AZURE_STORAGE_CONNECTION_STRING:
        return _save_to_azure(dest_path, file_obj, container)
    else:
        return _save_to_file_system(dest_path, file_obj, container)

def _save_to_file_system(dest_path, file_obj, container):
    fqp = os.path.join(settings.MEDIA_ROOT, container, dest_path)
    if not os.path.exists(os.path.dirname(fqp)):
        os.makedirs(os.path.dirname(fqp))

    with open(fqp, 'wb+') as dest_file:
            copyfileobj(file_obj, dest_file)

    uri = '{}{}/{}'.format(settings.MEDIA_URL, container, dest_path)
    return settings.INTERNAL_MEDIA_HOST + uri, site.build_full_url(uri)

def _save_to_azure(dest_path, file_obj, container):
    blob_service = BlockBlobService(connection_string=settings.AZURE_STORAGE_CONNECTION_STRING)

    blob_service.create_blob_from_stream(container, dest_path, file_obj)
    sas_token = blob_service.generate_blob_shared_access_signature(
        container,
        dest_path,
        BlobPermissions.READ,datetime.utcnow() + timedelta(hours=24*3000))
    blob_url = blob_service.make_blob_url(container, dest_path, sas_token=sas_token)
    return blob_url, blob_url