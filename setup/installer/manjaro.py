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

    logger.log("installing mongodb")
    execution.execute_command('sudo pacman install -S chrpath')    
    execution.execute_command('sudo pamac install php7-mongodb')

def dpkg_install() -> None:
    """
    function which installs dpkg

    Returns
    -------
    None
    """
    logger.log("installing dpkg")
    execution.execute_command('sudo pamac install dpkg')

def libgtk_install() -> None:
    """
    function which installs libgtk

    Returns
    -------
    None
    """
    logger.log("installing libgtk")
    execution.execute_command("sudo pamac install libgtk")
    execution.execute_command("sudo pamac search libgtk")


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

    logger.log("installing mongodb compass")
    
    execution.execute_command("sudo dpkg -d mongodb-compass_1.33.1_amd64.deb")
    execution.execute_command("sudo dpkg -i mongodb-compass_1.33.1_amd64.deb")
    execution.execute_command("sudo dpkg apt -get -f install mongodb-compass_1.33.1_amd64.deb")

def influx_db_install() -> None:
    """
    function which installs influx db

    Returns
    -------
    None
    """
    logger.log("installing influxdb")
    execution.execute_command('sudo pamac install influxdb')


def epm() -> None:
    logger.log("installing epm")
    execution.execute_command("sudo pamac install epm")
    logger.log("installing rpm")
    execution.execute_command("sudo pamac install rpm")
    logger.log("installing server-6.0")
    execution.execute_command("sudo rpm --import https://www.mongodb.org/static/pgp/server-6.0.asc")
    logger.log("installing zypper")
    execution.execute_command("wget http://download.opensuse.org/distribution/13.2/repo/oss/suse/i586/zypper-1.11.14-2.1.i586.rpm")
    
    command = "sudo rpm -ivh zypper-1.11.14-2.1.i586.rpm"
    logger.log(f"executing command {command}")
    execution.execute_command(command)

def install_sl() ->None:
    """
    function which installs sl

    Returns
    -------
    None
    """
    command = "git clone https://aur.archlinux.org/yay.git"
    logger.log(f"executing command {command}")
    execution.execute_command(command)

    command = "cd yay"
    logger.log(f"executing command {command}")
    execution.execute_command(command)

    command = "makepkg -si"
    logger.log(f"executing command {command}")
    execution.execute_command(command)

    command = "pamac install sl"
    logger.log(f"executing command {command}")
    execution.execute_command(command)