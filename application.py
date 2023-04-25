import client, server
from utils import utils

def Main():
    # If server flag is included (-s or --server) run as server
    if utils.checkMode() == "server":
        return server.Main()
    # Else run as client
    client.Main()
    
# Code execution starts here
if __name__ == "__main__":
    Main()