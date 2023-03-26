import logging
import os 
import sys
from enum import Enum

def create_logger(logging_level : str = None) -> logging.Logger:
    """
    function which creates and returns a logger object

    Parameters
    ----------
    first : logging_level
        the 1st param, by default gets the environment variable $LOGGING_LEVEL which is specified in setup.sh

    Returns
    -------
    logging.Logger
        a logger object
    """


    if (logging_level == None):
        value = os.environ.get("LOGGING_LEVEL")
        if (value == None):
            logging_level = "INFO"
        else:
            logging_level = value
        
    logging.basicConfig(filename="setuplog.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    logger = logging.getLogger()
    logging.getLogger()
    match logging_level:
        case "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        case "WARNING":
            logger.setLevel(logging.WARNING)
        case "INFO":
            logger.setLevel(logging.INFO)
        case "DEBUG":
            logger.setLevel(logging.DEBUG)
        case "NOTSET":
            logger.setLevel(logging.CRITNOTSETICAL)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger

LOGGER = create_logger()
level = Enum("level", ["INFO", "WARNING", "ERROR"])

def log(message : str, level : level = level.INFO ) -> None:
    """
    function that logs information

    Parameters
    ----------
    first : message
        the 1st param, the information that will be logged
    second : level
        the 2nd param, in which level the message will be logged

    Returns
    -------
    None
    """
    match level:
        case level.INFO:
            LOGGER.info(message)
        case level.WARNING:
            LOGGER.warn(message)
        case level.ERROR:
            LOGGER.error(message)
        case _:
            raise Exception("logging level not recognized")