import logger.logger as logger
import execution.exeuction as execution
import platform
import distro
import installer.ubuntu as ubuntu
import installer.macos as macos

def main() -> None:
    """
    main function for the script
    """
    logger.log("Starting the installation")

    match platform.system():
        case "Darwin":
            macos.mongo_db_install()
            macos.influx_db_install()
            macos.grafana_install()
            macos.mongo_db_compass_install()
        case "Linux":
            distro_name, _, _ = distro.linux_distribution(full_distribution_name=False)

            match distro_name:
                case "ubuntu":
                    ubuntu.mongo_db_install()
                    ubuntu.mongo_db_compass_install()
                    ubuntu.influx_db_install()
                    ubuntu.grafana_install()
                

if __name__ == "__main__":
    main()




