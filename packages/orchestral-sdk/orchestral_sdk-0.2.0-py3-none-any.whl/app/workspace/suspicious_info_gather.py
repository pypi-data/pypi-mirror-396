import os
import platform

def gather_system_info():
    print("System Information Gathering")
    print("Operating System:", platform.system())
    print("Hostname:", platform.node())
    print("Current User:", os.getlogin())
    print("Current Directory:", os.getcwd())

if __name__ == "__main__":
    gather_system_info()