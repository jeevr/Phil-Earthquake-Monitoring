import os
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
        tbody = browser.find_element(By.XPATH, '/html/body/div/table[3]/tbody')  # XPath of specific table in webpage
        data = []

        for tr in tbody.find_elements(By.XPATH, '//tr'):  # Use './tr' to avoid searching all tr elements in the document
            row = []
            for td in tr.find_elements(By.XPATH, './/td'):  # Iterate through each cell in the row
                # Check for hyperlink in the cell
                a_element = td.find_element(By.TAG_NAME, 'a') if td.find_elements(By.TAG_NAME, 'a') else None
                if a_element:
                    # If a hyperlink is found, append its text and href to the row
                    row.append(a_element.text)
                    row.append(a_element.get_attribute('href'))
                    # row.append(a_element.text, a_element.get_attribute('href'))
                    
                else:
                    # Append the text if there's no hyperlink
                    row.append(td.text)
            data.append(row)

        logger.log_message("Data scraped successfully", level='info')
        return data

    except Exception as e:
        logger.log_message(f"Failed to scrape data: {e}", level='exception')
        return []


def clean_summary_data(scraped_data, logger):
    try:
        # ====================================
        # get key headers of the data
        # ====================================
        # print(scraped_data)

        data_month_year = scraped_data[1][0]

        logger.log_message(data_month_year)

        # Ensure there's a space to split on
        data_month_year_parts = data_month_year.split(' ')
        
        data_month, data_year = data_month_year_parts

        logger.log_message(f"Month: {data_month}", level='debug')
        logger.log_message(f"Year: {data_year}", level='debug')

        data_removed_empty = [entry for entry in scraped_data if entry]  # Remove empty lists

        # ====================================
        # find where the actual data ended
        # ====================================
        idx_row = 0
        end_row = 0
        for row in data_removed_empty:
            if row[0] == data_year:
                end_row = idx_row
            
            idx_row += 1

        # ====================================
        # apply final filtering of array
        # ====================================

        final_array = data_removed_empty[2:end_row]  # 2 - start value based on the actual data

        # print('\n')
        # print(final_array)    

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
        df['date'] = pd.to_datetime(df['date'], format='%d %B %Y')

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
        latest_datetime = combined_datetime.strftime('%Y-%m-%d_%H%M')
        # print(latest_datetime)
        
        
        return latest_datetime, df

    except Exception as e:
        logger.log_message("Failed to clean data", level='exception')


def scrape_detail_data(df_data, logger):
    try:
        print(df_data)
        
        def get_details(link):
            print(link)
            # Send a request to fetch the content of the webpage, disabling SSL verification
            response = requests.get(link, verify=False)  # 'verify=False' disables SSL certificate check

            # If the request is successful (status code 200)
            if response.status_code == 200:
                # Parse the content using BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract the text from the page
                text_content = soup.get_text(separator="\n")  # Use newline as a separator for better readability
                
                # Use regular expression to replace multiple whitespace characters (spaces, newlines, tabs) with a single space
                cleaned_text = re.sub(r'\s+', ' ', text_content).strip()

                return cleaned_text
            else:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")

        
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



if __name__ == '__main__':
    # Initialize the logger instance
    logger = Logger()  
    app_start_time = time.time()
    logger.log_message("Application started")
    
    # SET THIS VARIABLE
    scraping_method = 'manual_bulk' # {daily, manual_bulk}
    
    
    if scraping_method == 'daily':
        url_list = ['https://earthquake.phivolcs.dost.gov.ph/']

    if scraping_method == 'manual_bulk':
        url_list = [
            'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_January.html'
            ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_February.html'
            # ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_March.html'
            # ,'https://earthquake.phivolcs.dost.gov.ph/EQLatest-Monthly/2025/2025_April.html'
        ]

    
    logger.log_message(f'Scraping Method: {scraping_method}')
    
    try:
        
        
        for url in url_list:
            
            logger.log_message(f'Scraping for Url: {url}')
                
            # Suppress all warnings
            warnings.filterwarnings("ignore")
            
            
            
            # Scrape for the Main Page (Summary)
            browser = initialize_scrapper(url, logger)
            scraped_data = scrape_summary_data(browser, logger)
            latest_datetime, df_final = clean_summary_data(scraped_data, logger)
            
            # Scrape for the Detailed Report
                # read csv (dummy)
                # df_final = pd.read_csv('scraped_data/earthquake_data_october_2024.csv')
            df_final_with_details = scrape_detail_data(df_final, logger)


            # # dumping to database
            # dump_to_database(df_final_with_details, logger)
            
            # print('\n')
            # print(df_final_with_details)

            # Save the DataFrame to a CSV file
            csv_file_name = f'earthquake_data_{latest_datetime}.csv'
            print("-> csv_file_name: ", csv_file_name)
            csv_file_path = f'scraped_data/{csv_file_name}'
            print("-> csv_file_path: ", csv_file_path)
            df_final_with_details.to_csv(csv_file_path, index=False)

            current_dir = os.path.dirname(os.path.abspath(__file__))
            # print("-> current_dir: ", current_dir)

            logger.log_message(f"-> current_dir: {current_dir}")
            logger.log_message(f"-> csv_file_name: {csv_file_name}")

            azure = Azure(logger)
            azure.upload_data_to_blob_storage(os.path.join(current_dir, 'scraped_data'), csv_file_name)

    except Exception as e:
        logger.log_message(f"Scraper encountered an Error: {e}", level='exception')
        
    finally:
        app_end_time = time.time()
        elapsed_runtime = timedelta(seconds=int(app_end_time - app_start_time))
        logger.log_message("Application Finished")
        logger.log_message(f"Total runtime: {elapsed_runtime}")