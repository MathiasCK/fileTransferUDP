import socket
from utils import utils, arguments, header
import hashlib

def send_ack(sock, addr, seq_num):
    ack = f"ACK{seq_num}"
    sock.sendto(ack.encode(), addr)

def recv_packet(sock):
    data, addr = sock.recvfrom(1470)
    header, payload = data[:10], data[10:]
    seq_num, checksum = header.decode().split('|')
    return int(seq_num), payload, checksum, addr

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
    expected_seq_num = 0

    while True:
        seq_num, _, _, addr = recv_packet(server)
        print(seq_num)

        if seq_num == -1:
            break

        if seq_num == expected_seq_num:
            send_ack(server, addr, seq_num)
            expected_seq_num += 1

        continue
        # Receive packet from client
        data, client = server.recvfrom(1472)
        
        headers = data[:12]
        seq, ack, flags, win = header.parse_header (headers)
        synFlag, ackFlag, finFlag = header.parse_flags(flags)

        if win == 5:
            print(seq)
            server.sendto(str(ack).encode(), client)
            expected_seq_num += 1
            continue


        if synFlag == 8:
            packet = header.create_packet(0, 0, 12, 0, b'')
            server.sendto(packet, client)
            continue

        if finFlag == 2:
            break

        # Check if packet is not the expected packet
        if seq != ex_packetNum:
            utils.invalidPacket(seq, 'Received out of order')
            continue

        if ackFlag != 4:
            continue;
        
        # Handle client data
        print(f"Received packet {ack}")
        server.sendto(str(ack).encode(), client)
        
        # Update expected packet value
        ex_packetNum += 1
        
    # Send ack & close socket
    # packet = header.create_packet(ex_packetNum, seq, 4, 0, b'')
    # server.sendto(packet, client)
    server.close()

if __name__ == '__main__':
    Main()
