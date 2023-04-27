import socket
from utils import arguments, data_handlers, utils, header, responses

# Test client-server connection
# @client_sd -> client socket
# @ip -> server ip address
# @port -> server port
# @reliability -> value provided in -r flag (default None)
def connectClient(client_sd, ip, port, reliability):
    try:
        # Send and encode reliability value to server
        data = str(reliability).encode()
        # See utils.createAndSendPacket()
        utils.createAndSendPacket(client_sd, (ip, port), 0, 0, 8, 0, data)
        # Receibe data from client
        data, _ = client_sd.recvfrom(1472)
        # Extract headers (first 12 bytes)
        headers = data[:12]
        # Extract flags from header
        # See -> header.parse_header
        _, _, flags, _ = header.parse_header (headers)

        # If server sends 1 flag it indicates the server reliability does not match the client reliability
        if flags == 1:
            # Extract data
            data = data[12:].decode()
            # See -> responses.connectionRefused()
            responses.connectionRefused(data)

        # If flag is not 12 (SYN/ACK flag) the connection was not sucessfull
        if flags != 12:
            # See -> responses.connectionRefused()
            responses.connectionRefused({})
        # Print success message
        print("-------------------------------------------------------------")
        print(f"A UDP client connected to server {ip}, port {port}")
        print("-------------------------------------------------------------")
    except Exception as err:
        # See -> responses.err()
        responses.err(err)

# Code execution starts here
def Main():
    # Create client socket
    client_sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Get client optional arguments (see arguments.py -> checkClientOpts)
    ip, port, file, trigger, reliability = arguments.checkClientOpts()

    # See -> connectClient()
    connectClient(client_sd, ip, port, reliability)
    # See utils -> data_handlers.handleClientData()
    data_handlers.handleReliability(client_sd, (ip, port), file, trigger, reliability)

if __name__ == '__main__':
    Main()
