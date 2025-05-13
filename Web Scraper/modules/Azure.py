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
        
    def upload_data_to_blob_storage(self, source_file, blob_folder_path, blob_file_name):
        try:
            if self.logger is not None: # to avoid dependency error
                self.logger.log_message(f"Uploading to Azure Blob Storage: {self.storage_acct_name}")
                self.logger.log_message(f"Uploading to Azure Blob Container: {self.container_name}")

            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)          

            # source_file = os.path.join(source_folder_path, file)
            blob_file_path = os.path.join(blob_folder_path, blob_file_name).replace("\\", "/")  # Normalize for URL path
            
            print(source_file)
            print(blob_file_path)
        
            with open(source_file, "rb") as data:
                container_client.upload_blob(name=blob_file_path, data=data, overwrite=True)
                print(f"Uploaded '{blob_file_name}' to container path: '{blob_file_path}'")

            if self.logger:
                self.logger.log_message(f"Uploaded '{blob_file_name}' to container path: '{blob_file_path}'")
            
        except Exception as e:
            if self.logger is not None: # to avoid dependency error
                self.logger.log_message(f"Failed to upload to Azure Blob: {e}", level='exception')
            
    
        
    
# if __name__ == '__main__':
#     from datetime import datetime
    
#     # for testing only
#     # sample file date 
#     date_str = "2024-01-31_2304"
    
#     local_folder = r'Z:\Projects\Phil-Earthquake-Monitoring\Web Scraper\scraped_data'
#     file = f'earthquake_data_latest_datapoint_{date_str}.csv'
#     azure = Azure()
    
#     source_file = os.path.join(os.path.join(local_folder, file))
    
    
#     parsed_date = datetime.strptime(date_str, '%Y-%m-%d_%H%M')

#     year = parsed_date.year      
#     month = parsed_date.month    
#     day = parsed_date.day         
#     latest_time = parsed_date.strftime('%H%M')
    
#     # 0 padding
#     year_str = str(year)              
#     month_str = f"{month:02d}"        
#     day_str = f"{day:02d}"      
    
#     print(azure.storage_acct_name)
#     print(azure.storage_acct_key)
#     print(azure.connection_string)
#     print(azure.container_name)
    
    
#     blob_root_fodler = 'bronze'
#     blob_folder_path = f'{blob_root_fodler}/year={year_str}/month={month_str}/day={day_str}/'
#     blob_file_name = f'earthquake_data_latest_datapoint_{latest_time}.csv'
    
#     azure.upload_data_to_blob_storage(source_file, blob_folder_path, blob_file_name)