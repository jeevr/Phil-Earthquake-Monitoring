import logging
import time
import os
from datetime import datetime



class Logger:
    def __init__(self, log_dir = 'logs', log_file_base='scraper_log.txt'):
        os.makedirs(log_dir, exist_ok=True)
        self.error_occurred = False
        self.log_dir = log_dir
        self.log_file_base = log_file_base
        self.start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_log_name = f"{log_file_base}_{self.start_time}_temp.txt"
        self.final_log_path = None
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Set the overall logging level

        # Create log file with dynamic name based on date and time
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_name = f'{self.log_file_base}_{current_time}.txt'

        # Create handlers
        self.file_handler = logging.FileHandler(os.path.join(self.log_dir, self.temp_log_name))
        self.console_handler = logging.StreamHandler()

        # Set log level for handlers
        self.file_handler.setLevel(logging.DEBUG)
        self.console_handler.setLevel(logging.INFO)

        # Create formatters and add them to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)

    def log_message(self, message, level='info'):
        """Logs messages to the log file with specified logging level."""
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.error_occurred = True
            self.logger.error(message)
        elif level == 'exception':
            self.error_occurred = True
            self.logger.exception(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'debug':
            self.logger.debug(message)
        else:
            self.logger.info(message) # Default to info
            
    def finalize_log(self):
        """Renames the log file based on error status."""
        suffix = " - Error" if self.error_occurred else ""
        final_name = f"{self.log_file_base}_{self.start_time}{suffix}.txt"
        final_path = os.path.join(self.log_dir, final_name)

        # Close and rename log file
        self.file_handler.close()
        self.logger.removeHandler(self.file_handler)
        os.rename(os.path.join(self.log_dir, self.temp_log_name), final_path)
        self.final_log_path = final_path
        return final_path
    
    
    
# if __name__ == "__main__":
#     # testing the class
    
#     from time import sleep

#     log = Logger()

#     try:
#         log.log_message("Starting scraper...", "info")
#         # Simulate process
#         sleep(1)
#         # raise ValueError("Something went wrong!")  # Simulate error
        
#         log.log_message("Scraper Finished")
#     except Exception as e:
#         log.log_message(f"Error occurred: {e}", "exception")
#     finally:
#         log_path = log.finalize_log()
#         print(f"Log saved at: {log_path}")
