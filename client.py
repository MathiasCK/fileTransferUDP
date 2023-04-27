import socket
from utils import arguments, data_handlers, utils, header, responses

def connectClient(client_sd, ip, port, reliability):
    try:
        data = str(reliability).encode()

        utils.createAndSendPacket(client_sd, (ip, port), 0, 0, 8, 0, data)

        data, _ = client_sd.recvfrom(1472)
        headers = data[:12]

        _, _, flags, _ = header.parse_header (headers)
        
        synFlag, ackFlag, _ = header.parse_flags(flags)

        if flags == 1:
            data = data[12:].decode()
            responses.connectionRefused(data)

        if synFlag + ackFlag != 12:
            responses.connectionRefused({})
        # Print success message
        print("-------------------------------------------------------------")
        print(f"A UDP client connected to server {ip}, port {port}")
        print("-------------------------------------------------------------")
    except Exception as err:
        responses.err(err)

def Main():
    # Create client socket
    client_sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Get client optional arguments (see arguments.py -> checkClientOpts)
    ip, port, file, trigger, reliability = arguments.checkClientOpts()

    # See utils -> connectClient()
    connectClient(client_sd, ip, port, reliability)
    # See utils -> data_handlers.handleClientData()
    data_handlers.handleReliability(client_sd, (ip, port), file, reliability)

if __name__ == '__main__':
    Main()
