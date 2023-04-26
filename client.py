import socket
from utils import arguments, data_handlers

def Main():
    # Create client socket
    client_sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Get client optional arguments (see arguments.py -> checkClientOpts)
    ip, port, file, trigger, reliability = arguments.checkClientOpts()

    # See utils -> data_handlers.connectClient()
    data_handlers.connectClient(client_sd, ip, port, reliability)
    # See utils -> data_handlers.handleClientData()
    data_handlers.handleClientData(client_sd, (ip, port), file, reliability)

if __name__ == '__main__':
    Main()
