import os
import json
from azure.storage.blob import BlobServiceClient


class Azure:
    def __init__(self, logger=None):
        # Configure logger
        self.logger = logger
        self.config_path = 'azure_config.json'
        self.azure_config = self.get_azure_config()
        
        # get creds
        self.storage_acct_name = self.get_config_value('azure-blob-storage', 'STORAGE_ACCT_NAME')
        self.storage_acct_key = self.get_config_value('azure-blob-storage', 'STORAGE_ACCT_KEY')
        self.connection_string = self.get_config_value('azure-blob-storage', 'CONNECTION_STRING')
        self.container_name = self.get_config_value('azure-blob-storage', 'CONTAINER_NAME')
    

    def get_azure_config(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, self.config_path)
        
        with open(self.config_path, 'r') as file:
            return json.load(file)
        
    def get_service_config(self, service_key):
        try:
            return self.azure_config['azure'][service_key]
        except KeyError:
            raise ValueError(f"Service key '{service_key}' not found in configuration.")

    def get_config_value(self, service_key, param_key):
        service_config = self.get_service_config(service_key)
        try:
            return service_config[param_key]
        except KeyError:
            raise ValueError(f"Parameter key '{param_key}' not found for service '{service_key}'.")
        
    def upload_data_to_blob_storage(self, folder_path, file):
        try:
            if self.logger is not None: # to avoid dependency error
                self.logger.log_message(f"Uploading to Azure Blob Storage: {self.storage_acct_name}")
                self.logger.log_message(f"Uploading to Azure Blob Container: {self.container_name}")

            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)          

            file_path = os.path.join(folder_path, file)

            # Define virtual blob path (including folders if needed)
            blob_path = os.path.join(folder_path, file).replace("\\", "/")  # Normalize for URL path
        
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_path, data=data, overwrite=True)

            if self.logger:
                self.logger.log_message(f"Uploaded '{file}' to container path: '{blob_path}'")
            
        except Exception as e:
            if self.logger is not None: # to avoid dependency error
                self.logger.log_message(f"Failed to upload to Azure Blob: {e}", level='exception')
    
        
    
if __name__ == '__main__':
    # for testing only
    local_folder = r'Z:\Projects\Phil-Earthquake-Monitoring\Web Scraper\scraped_data'
    file = 'earthquake_data_may_2025.csv'
    azure = Azure()
    
    print(azure.storage_acct_name)
    print(azure.storage_acct_key)
    print(azure.connection_string)
    print(azure.container_name)
    
    
    azure.upload_data_to_blob_storage(local_folder, file)