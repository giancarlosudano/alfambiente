import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def get_service_client():
	storage_connection_string : str = os.getenv("AZURE_BLOB_CONNECTION_STRING") or ""
	blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
	return blob_service_client

def get_container_client(container : str):
	storage_connection_string : str = os.getenv("AZURE_BLOB_CONNECTION_STRING") or ""
	blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
	container_client = blob_service_client.get_container_client(container)
	return container_client

def get_blob_client(container :str, blob_name: str):
	storage_connection_string : str = os.getenv("AZURE_BLOB_CONNECTION_STRING") or ""
	blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
	blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
	return blob_client

def get_blob_content(container :str, blob_name : str):
	blob_client = get_blob_client(container, blob_name)
	blob_content = blob_client.download_blob().readall()
	blob_content_decoded = blob_content.decode("utf-8")
	return blob_content_decoded

def get_connectionstring():
	storage_connection_string : str = os.getenv("AZURE_BLOB_CONNECTION_STRING") or ""
	return storage_connection_string

def fix_url(url: str):
	return url.replace("C:/Users/gisudano/OneDrive - Microsoft/Desktop/Prototypes/RFP Copilot/dyn365_custeng\\", "")