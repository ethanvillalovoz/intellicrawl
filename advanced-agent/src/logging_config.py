import logging

def setup_logging():
    """
    Configure the logging settings for the application.

    Sets the logging level to INFO and specifies the log message format.
    Logs are output to the console via StreamHandler.
    """
    logging.basicConfig(
        level=logging.INFO,  # Set log level to INFO
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  # Log message format
        handlers=[
            logging.StreamHandler()  # Output logs to the console
        ]
    )