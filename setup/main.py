import logger.logger as logger
import execution.exeuction as execution
import platform
import distro
import installer.ubuntu as ubuntu

def main() -> None:
    """
    main function for the script
    """
    logger.log("Starting the installation")

    match platform.system():
        case "Darwin":
            pass
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




