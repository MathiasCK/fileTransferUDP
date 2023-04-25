import socket
from utils import arguments, data_handlers

def Main():
    # Create client socket
    client_sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Get client optional arguments (see arguments.py -> checkClientOpts)
    ip, port, file = arguments.checkClientOpts()

    # See utils -> data_handlers.handleClientData()
    data_handlers.connectClient(client_sd, ip, port, file)

    # Close socket
    client_sd.close()

if __name__ == '__main__':
    Main()
