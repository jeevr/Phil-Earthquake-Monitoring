import os
from azure.storage.blob import BlobServiceClient


STORAGE_ACCT_KEY = '3ak/TDuk0zTkwWxSzadAMcbX/z8pw0Apy2Yi5Z7xsmK7yfLpvJRl4grR9QGIkycMCXYiB9dwLXPM+AStcIRS6g=='
STORAGE_ACCT_NAME = 'earthquakedatastorage'
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=earthquakedatastorage;AccountKey=3ak/TDuk0zTkwWxSzadAMcbX/z8pw0Apy2Yi5Z7xsmK7yfLpvJRl4grR9QGIkycMCXYiB9dwLXPM+AStcIRS6g==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = 'scraped-data'



class Azure:
    def __init__(self, logger=None):
        # Configure logger
        self.logger = logger

    def get_azure_config(self):
        pass 
    
    def upload_data_to_blob_storage(self, folder_path, file):
        try:
            self.logger.log_message(f"Uploading to Azure Blob Storage: {STORAGE_ACCT_NAME}")
            self.logger.log_message(f"Uploading to Azure Blob Container: {CONTAINER_NAME}")

            blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)          

            file_path = os.path.join(folder_path, file)

            with open(file_path, "rb") as data:
                container_client.upload_blob(file, data, overwrite=True)

        except Exception as e:
            self.logger.log_message(f"Failed to upload to Azure Blob: {e}", level='exception')
            


# if __name__ == '__main__':
#     azure = Azure()
#     azure.upload_data_to_blob_storage('Z:\Projects\PhilEarthQuakeMonitoring\PhilippineEarthquakeWebScrapper\scraped_data', 'earthquake_data_october_2024.csv')