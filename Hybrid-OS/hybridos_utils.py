import os
import platform
import getpass

def list_files(directory):
    try:
        items = os.listdir(directory)
        if not items:
            return "Directory is empty."
        return "\n".join(items)
    except PermissionError:
        return "Permission denied to access this directory."
    except FileNotFoundError:
        return "Directory not found."

def system_info():
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Platform": platform.platform(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "User": getpass.getuser()
    }
    return "\n".join([f"{key}: {value}" for key, value in info.items()])
