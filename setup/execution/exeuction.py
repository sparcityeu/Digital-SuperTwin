import subprocess

def execute_command(command : str) -> int:
    """
    function which executes a command and returns the return code

    Parameters
    ----------
    first : command
        the 1st param, the command which will be executed by the function

    Returns
    -------
    int
        return code of the executed command
    """
    return subprocess.run(command, shell=True).returncode

