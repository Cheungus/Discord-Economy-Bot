import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level to DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the log message format
        datefmt='%Y-%m-%d %H:%M:%S'  # Set the date format
    )

    # Optionally, configure specific loggers
    logging.getLogger('discord').setLevel(logging.DEBUG)
    #logging.getLogger('asyncio').setLevel(logging.DEBUG)
    #logging.getLogger('asyncpg').setLevel(logging.DEBUG)