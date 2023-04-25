import socket
from utils import utils, arguments, data_handlers, header

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
    ex_ack = 0

    while True:
        # Receive packet from client
        data, client = server.recvfrom(1460)

        if data == b"CONNREQ":
            server.sendto("ACK".encode(), client)
            continue
        
        headers = data[:12]
        seq, ack, flags, win = header.parse_header (headers)

        print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}')

        if data == b"ACK/BYE" or b"ACK/BYE" in data:
            if ex_ack != ack:
                continue
            break

        # Check if packet is not the expected packet
        if seq != ex_packetNum:
            utils.invalidPacket(seq, 'Received out of order')
            continue
        
        # See utils -> data_handlers.handleClientData()
        data_handlers.handleClientData(ack, server, client)
        
        # Update expected packet value
        ex_packetNum += 1
        ex_ack += 1
        
    # Close socket
    server.close()

if __name__ == '__main__':
    Main()
