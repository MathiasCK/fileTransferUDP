import socket
from utils import utils, arguments, data_handlers

def Main():
    # See utils -> arguments.checkServerOpts()
    bind, port = arguments.checkServerOpts()
    # Set up server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind server socket
    server.bind((bind, port))

    # Print success message
    print("---------------------------------------------")
    print(f"A UDP server is listening on port {str(port)}")
    print("---------------------------------------------")

    # Keep track of expected incomming packet
    ex_packetNum = 0

    while True:
        # Receive packet from client
        data, client = server.recvfrom(1024)

        if data == b"CONNREQ":
            server.sendto("ACK".encode(), client)
            continue
        
        if data == b"ACK/BYE":
            break

        # Extract packet fields
        packetNum, checksum, payload = utils.decodePacket(data)

        # Verify checksum
        if not utils.validateCheckSum(payload, checksum):
            utils.invalidPacket(packetNum, 'Checksum failed')
            continue

        # Check if packet is not the expected packet
        if packetNum != ex_packetNum:
            utils.invalidPacket(packetNum, 'Received out of order')
            continue
        
        # See utils -> data_handlers.handleClientData()
        data_handlers.handleClientData(packetNum, server, client)
        # Update expected packet value
        ex_packetNum += 1
        
    # Close socket
    server.close()

if __name__ == '__main__':
    Main()
