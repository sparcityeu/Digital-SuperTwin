import logger.logger as logger
import execution.exeuction as execution
import platform

def prepare() -> None:
    """
    function which prepares mac for installing necessary packages by installing xcode developer tools and homebrew
    """
    logger.log("installing xcode developer tools")
    execution.execute_command("xcode-select --install")

    logger.log("installing homebrew")
    execution.execute_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

    

def mongo_db_install() -> None:
    """
    function which installs mongo db

    Returns
    -------
    None
    """
    logger.log("tapping mongodb homebrew tap")
    execution.execute_command('brew tap mongodb/brew')

    logger.log("updating homebrew")
    execution.execute_command('brew update')

    logger.log("installing mongodb")
    execution.execute_command('brew install mongodb-community@6.0')

def mongo_db_compass_install() -> None:
    """
    function which installs mongo db compass

    Returns
    -------
    None
    """
    logger.log("please install mongodb compass using this link: https://www.mongodb.com/docs/compass/current/install/")
     

def influx_db_install() -> None:
    """
    function which installs influx db

    Returns
    -------
    None
    """
    logger.log("installing influxdb")
    execution.execute_command('brew install influxdb')

def grafana_install() -> None:
    """
    function which installs grafana

    Returns
    -------
    None
    """
    logger.log("installing grafana")
    execution.execute_command('brew install grafana') 