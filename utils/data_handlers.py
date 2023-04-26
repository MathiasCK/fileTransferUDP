import socket
from utils import responses, header, utils

def sendData(client_sd, ip, port, file_path, reliability):

    with open(file_path, 'rb') as file:
        
        sequence_number = 0
        ex_ack = 0

        if reliability is not None:
            if reliability == 'SAN':
                return utils.stop_and_wait(client_sd, sequence_number, ex_ack, file, ip, port)

        while True:
            # Read next chunk from file
            chunk = file.read(1460)

            packet = header.create_packet(sequence_number, ex_ack, 4, 0, chunk)
            
            client_sd.sendto(packet, (ip, port))

            ack_received = False

            while not ack_received:
                try:
                    client_sd.settimeout(1)
                    ack, _ = client_sd.recvfrom(1472)

                    if int(ack.decode()) == sequence_number:
                        ack_received = True
                        print(f"Packet {sequence_number} sent")
                        sequence_number += 1
                        ex_ack += 1

                except socket.timeout:
                    print(f"Packet {sequence_number} timed out - Resending packet")
                    client_sd.sendto(packet.encode(), (ip, port))

            if not chunk:
                packet = header.create_packet(sequence_number, sequence_number, 2, 0, chunk)
                client_sd.sendto(packet, (ip, port))
                break
    client_sd.close()

def connectClient(client_sd, ip, port, file, reliability):
    try:
        packet = header.create_packet(0, 0, 8, 0, b'')
        client_sd.sendto(packet, (ip, port))

        data, _ = client_sd.recvfrom(1472)
        headers = data[:12]

        _, _, flags, _ = header.parse_header (headers)
        synFlag, ackFlag, _ = header.parse_flags(flags)
        
        if synFlag + ackFlag != 12:
            responses.connectionRefused({})
        # Print success message
        print("-------------------------------------------------------------")
        print(f"A UDP client connected to server {ip}, port {port}")
        print("-------------------------------------------------------------")
    except Exception as err:
        responses.err(err)

    sendData(client_sd, ip, port, file, reliability)

def handleClientData(ack, server, client, data):
    print(f"Received packet {ack}")
    server.sendto(str(ack).encode(), client)