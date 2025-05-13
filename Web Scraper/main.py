import os
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager # Used for updating the Web Driver based on the Current Web Browser Version
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import warnings
import re
from datetime import datetime, timedelta
import json


# custom modules import
from modules.Logger import Logger
from modules.DBConnect import DBConnect # 0.1
from modules.Azure import Azure



def initialize_scrapper(url, logger):
    try:
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        # edge_driver_path = os.path.join(os.getcwd(), 'edgedriver_win64', 'msedgedriver.exe')
        # edge_service = Service(edge_driver_path)

        # Automatically downloads correct driver for installed browser
        edge_service = Service(EdgeChromiumDriverManager().install())
        edge_options = Options()

        # edge_options.add_argument(f'user-agent={user_agent}')

        browser = webdriver.Edge(service=edge_service, options=edge_options)
        browser.get(url)

        logger.log_message("Page loaded successfully", level='info')
        time.sleep(2)  # give time to load the page

        return browser

    except Exception as e:
        logger.log_message("Failed to initialize scraper", level='exception')
        return None


def scrape_summary_data(browser, logger):
    """
    Scrapes data from the specified table on the webpage.

    Parameters:
        browser: The Selenium WebDriver instance.
        logger: The logger instance to log messages.

    Returns:
        list: A list of lists containing the scraped data along with hyperlinks.
    """
    try:
        # Wait for the table body to load
        tbody = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/table[3]/tbody'))
        )
        data = []

        # Use './tr' instead of '//tr' to scope to just tbody
        rows = tbody.find_elements(By.XPATH, './tr')

        for row_index, tr in enumerate(rows):
            try:
                row_data = []
                tds = tr.find_elements(By.XPATH, './td')

                for td_index, td in enumerate(tds):
                    try:
                        a_elements = td.find_elements(By.TAG_NAME, 'a')
                        if a_elements:
                            # Append hyperlink text and URL
                            row_data.append(a_elements[0].text)
                            row_data.append(a_elements[0].get_attribute('href'))
                        else:
                            row_data.append(td.text)
                    except StaleElementReferenceException:
                        logger.log_message(f"Stale element at row {row_index}, column {td_index}. Retrying...", level='warning')
                        tds = tr.find_elements(By.XPATH, './td')  # Re-fetch the row cells
                        td = tds[td_index]
                        row_data.append(td.text)

                data.append(row_data)

                
                
            except Exception as row_error:
                logger.log_message(f"Error processing row {row_index}: {row_error}", level='warning')

        logger.log_message("Data scraped successfully", level='info')
        logger.log_message(f"data: {data}", level='debug')
        
        return data

    except Exception as e:
        logger.log_message(f"Failed to scrape data: {e}", level='exception')
        return []

def clean_summary_data(scraped_data, logger):
    try:
   
        # ====================================
        # apply final filtering of array
        # ====================================

        final_array =[row for row in scraped_data if row]

        # Define headers
        df_headers = ['date_time', 'hlink', 'latitude', 'longitude', 'depth_km', 'magnitude', 'location']

        # Convert the sliced list to a DataFrame
        df = pd.DataFrame(final_array, columns=df_headers)
        
        # Extract any non-digit prefix (symbols)
        df['depth_km_symbol'] = df['depth_km'].astype(str).str.extract(r'^(\D+)')
        
        # Extract digits only and convert to numeric
        df['depth_km'] = (
            df['depth_km']
            .astype(str)
            .str.extract(r'(\d+)')
            .astype(float)
        )
        
        # Split the column into date and time
        df[['date', 'time']] = df['date_time'].str.split(' - ', expand=True)

        # Convert the 'date' column to datetime format
        # df['date'] = pd.to_datetime(df['date'], format='%d %B %Y') # old version
        df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True, errors='coerce') # fix for mix format

        # Convert the 'time' column to datetime format (24-hour format)
        df['time'] = pd.to_datetime(df['time'], format='%I:%M %p').dt.strftime('%H:%M:%S')

        # Convert data types
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
        df['depth_km'] = df['depth_km'].astype(float)
        df['magnitude'] = df['magnitude'].astype(float)

        # Rearranging the columns
        df = df[['date_time', 'date', 'time', 'latitude', 'longitude', 'depth_km', 'depth_km_symbol', 'magnitude', 'location', 'hlink']]

        # Get the first row's datetime
        first_row = df.iloc[0]

        # Extract date and time values
        date_value = pd.to_datetime(first_row['date']).date()
        time_value = pd.to_datetime(first_row['time']).time()
        
        # print("Date:", date_value)
        # print("Time:", time_value)

        # Combine date and time
        combined_datetime = datetime.combine(date_value, time_value)
        latest_date = combined_datetime.strftime('%Y-%m-%d')
        latest_time = combined_datetime.strftime('%H%M')
        latest_datetime = combined_datetime.strftime('%Y-%m-%d_%H%M')
        # print(latest_datetime)
        
        
        return latest_date, latest_time, latest_datetime, df

    except Exception as e:
        logger.log_message("Failed to clean data", level='exception')


def scrape_detail_data(df_data, logger):
    try:
        print(df_data)
        
        logger.log_message(f"Getting Scraped Details per Data Point.")
        
        def get_details(link):
            # print(link)
            # Send a request to fetch the content of the webpage, disabling SSL verification
            response = requests.get(link, verify=False)  # 'verify=False' disables SSL certificate check
            
            # placeholder
            cleaned_text = ''
            
            # If the request is successful (status code 200)
            if response.status_code == 200:
                # Parse the content using BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract the text from the page
                text_content = soup.get_text(separator="\n")  # Use newline as a separator for better readability
                
                # Use regular expression to replace multiple whitespace characters (spaces, newlines, tabs) with a single space
                cleaned_text = re.sub(r'\s+', ' ', text_content).strip()

            else:
                cleaned_text = '--- UNABLE TO RETRIEVE DATA FROM URL ---'
                
                logger.log_message(f"Failed to retrieve the link: {link}. Status code: {response.status_code}", "warning")

            return cleaned_text
        
            
        df_data['details'] = df_data['hlink'].apply(get_details)
    
        
        return df_data

    except Exception as e:
        logger.log_message(f"Failed to scrape data: {e}", level='exception')
        return []



def dump_to_database(df_data, logger):
    try:
        db_env = 'local_phil_earthquakes'   

        # connecting to database
        SqlConn = DBConnect.Connector(db_env)
        SqlConn.connect()


        df_data.to_sql('tbldaily_earthquake_data', SqlConn.engine, if_exists='replace', index = False, schema = 'raw', chunksize = 10000, method='multi')
        
        # Log confirmation
        logger.log_message(f"DataFrame Dumped Datbase", level='info')

    except Exception as e:
        logger.log_message(f"Failed to Dump to Database: {e}", level='exception')
    finally:
        SqlConn.disconnect()
        # pass


def generate_blob_folder_path(file_date):
    parsed_date = datetime.strptime(file_date, '%Y-%m-%d')
    
    # explode date parts
    year = parsed_date.year      
    month = parsed_date.month    
    day = parsed_date.day
    
    # 0 padding
    year_str = str(year)              
    month_str = f"{month:02d}"        
    # day_str = f"{day:02d}"          
    
    # folder path for blob storage
    blob_root_fodler = 'bronze'
    blob_sub_dir = 'scraped-data'
    # blob_folder_path = f'{blob_root_fodler}/{blob_sub_dir}/year={year_str}/month={month_str}/day={day_str}/'
    blob_folder_path = f'{blob_root_fodler}/{blob_sub_dir}/year={year_str}/month={month_str}/'
    
    return blob_folder_path


def get_current_file_dir():
    return os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    # Initialize the logger instance
    logger = Logger()  
    
    try:
        app_start_time = time.time()
        logger.log_message("Application started")
        
        # SET THIS VARIABLE
        scraping_method = 'manual_bulk' # {daily, manual_bulk}
        
        
        if scraping_method == 'daily':
            url_list = ['https://earthquake.phivolcs.dost.gov.ph/']

        if scraping_method == 'manual_bulk':
            url_list = [
                'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_January.html'
                ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_February.html'
                ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_March.html'
                ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_April.html'
                ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_May.html'
                ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2024/2024_June.html'
                
                # 'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_January.html'
                # ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_February.html'
                # ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_March.html'
                # ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_April.html'
            ]
            

        logger.log_message(f'Scraping Method: {scraping_method}')
    
        for url in url_list:
            try:
                logger.log_message(f'Started Scraping for Url: {url}')
                    
                # Suppress all warnings
                warnings.filterwarnings("ignore")
                
                # Scrape for the Main Page (Summary)
                browser = initialize_scrapper(url, logger)
                scraped_data = scrape_summary_data(browser, logger)
                latest_date, latest_time, latest_datetime, df_final = clean_summary_data(scraped_data, logger)
                
                # Scrape for the Detailed Report
                df_final_with_details = scrape_detail_data(df_final, logger)
                
                logger.log_message(f"Final Dataframe Ready")
                
                # # dumping to database
                # dump_to_database(df_final_with_details, logger)
                
                csv_file_name = f'earthquake_data_latest_datapoint_{latest_datetime}.csv'
                csv_local_file_path = f'scraped_data/{csv_file_name}'
                df_final_with_details.to_csv(csv_local_file_path, index=False)

                current_dir = get_current_file_dir()

                logger.log_message(f"-> current_dir: {current_dir}")
                logger.log_message(f"-> csv_file_name: {csv_file_name}")
                
                blob_folder_path = generate_blob_folder_path(latest_date)
                blob_file_name = f'earthquake_data_latest_datapoint_{latest_date}_{latest_time}.csv'
                
                logger.log_message(f"-> blob_folder_path: {blob_folder_path}")
                logger.log_message(f"-> blob_file_name: {blob_file_name}")
                
                azure = Azure(logger)
                # azure.upload_data_to_blob_storage(os.path.join(current_dir, 'scraped_data'), csv_file_name)
                azure.upload_data_to_blob_storage(os.path.join(current_dir, csv_local_file_path), blob_folder_path, blob_file_name)

                logger.log_message(f'Scraping for Url Finished')
                
            except Exception as e:
                logger.log_message(f"Encountered an Error: {e}", level='exception')
                logger.log_message(f"Skipping this Url: {url}", "warning")
                
                continue  # Skip to next URL
            
    except Exception as e:
        logger.log_message(f"Error occurred: {e}", "exception")
        
    finally:
        log_path = logger.finalize_log()
        print(f"Log saved at: {log_path}")
        app_end_time = time.time()
        elapsed_runtime = timedelta(seconds=int(app_end_time - app_start_time))
        logger.log_message("Application Finished")
        logger.log_message(f"Total runtime: {elapsed_runtime}")