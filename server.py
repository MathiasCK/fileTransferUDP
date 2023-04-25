import socket
from utils import utils, arguments, data_handlers, header

def Main():
    # See utils -> arguments.checkServerOpts()
    bind, port, trigger, reliability = arguments.checkServerOpts()
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
        data, client = server.recvfrom(1472)
        
        headers = data[:12]
        seq, ack, flags, win = header.parse_header (headers)
        synFlag, ackFlag, finFlag = header.parse_flags(flags)


        if synFlag == 8:
            packet = header.create_packet(0, 0, 12, 0, b'')
            server.sendto(packet, client)
            continue

        if finFlag == 2:
            if ex_ack != ack:
                continue
            break

        # Check if packet is not the expected packet
        if seq != ex_packetNum:
            utils.invalidPacket(seq, 'Received out of order')
            continue

        if ackFlag != 4:
            continue;
        
        # See utils -> data_handlers.handleClientData()
        data_handlers.handleClientData(ack, server, client, data)
        
        # Update expected packet value
        ex_packetNum += 1
        ex_ack += 1
        
    # Send ack & close socket
    packet = header.create_packet(ex_packetNum, ex_ack, 4, 0, b'')
    server.sendto(packet, client)
    server.close()

if __name__ == '__main__':
    Main()
