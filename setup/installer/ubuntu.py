import logger.logger as logger
import execution.exeuction as execution
import platform

def mongo_db_install() -> None:
    """
    function which installs mongo db

    Returns
    -------
    None
    """
    logger.log("Import the public GPG key")
    execution.execute_command("curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -")
    logger.log("create a file in the sources.list.d directory named mongodb-org-4.4.list")
    execution.execute_command('echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4     multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list')
    logger.log("update your server’s local package index")
    execution.execute_command("sudo apt update")
    logger.log("install MongoDB")
    execution.execute_command("sudo apt install mongodb")

def mongo_db_compass_install() -> None:
    """
    function which installs mongo db compass

    Returns
    -------
    None
    """

    if (platform.uname()[4] == "aarch64"):
        logger.log("Mongodb compass is not supported on Ubuntu while running on a ARM architecture, please install an alternative Mongodb GUI")
        return


    logger.log("Download the MongoDB compass .deb file")
    execution.execute_command("wget https://downloads.mongodb.com/compass/mongodb-compass_1.28.1_amd64.deb")
    logger.log("Install the .deb file")
    execution.execute_command("sudo apt install ./mongodb-compass_1.28.1_amd64.deb")
    logger.log("Open the application and click on the connect button.")

def influx_db_install() -> None:
    """
    function which installs influx db

    Returns
    -------
    None
    """
    logger.log("Download the GPG key")
    execution.execute_command("wget -qO- https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null")
    logger.log("Setup the repository")
    execution.execute_command("export DISTRIB_ID=$(lsb_release -si); export DISTRIB_CODENAME=$(lsb_release -sc)")
    logger.log("echo “deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable” | sudo tee /etc/apt/sources.list.d/influxdb.list > /dev/null")
    execution.execute_command("Update your server")
    logger.log("apt-get update")
    execution.execute_command("Install InfluxDB2")
    logger.log("apt-get install influxdb2")

def grafana_install() -> None:
    """
    function which installs grafana

    Returns
    -------
    None
    """
    # logger.log("Install the dependencies")
    # execution.execute_command("apt-get install wget curl gnupg2 apt-transport-https software-properties-common -y")
    # logger.log("Add the Grafana GPG key")
    # execution.execute_command("Add the Grafana repository")
    # logger.log("Update your server")
    # execution.execute_command("apt-get update")
    logger.log("Install Grafana")
    execution.execute_command("snap install grafana")