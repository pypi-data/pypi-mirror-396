import platform

def get_os():
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    return "linux"
