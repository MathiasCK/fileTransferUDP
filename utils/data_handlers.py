import socket
from utils import responses, header

def sendData(client_sd, ip, port, file_path):

    with open(file_path, 'rb') as file:
        sequence_number = 0

        while True:
            # Read next chunk from file
            chunk = file.read(1460)

            if not chunk:
                break

            packet = header.create_packet(sequence_number, 0, 0, 0, chunk)
            
            client_sd.sendto(packet, (ip, port))

            ack_received = False

            while not ack_received:
                try:
                    client_sd.settimeout(1)
                    data, _ = client_sd.recvfrom(1460)

                    if int(data.decode()) == sequence_number:
                        ack_received = True
                        print(f"Packet {sequence_number} sent")

                except socket.timeout:
                    print(f"Packet {sequence_number} timed out - Resending packet")
                    client_sd.sendto(packet.encode(), (ip, port))

            sequence_number += 1

        client_sd.sendto("ACK/BYE".encode(), (ip, port))
    
def connectClient(client_sd, ip, port, file):
    try:
        client_sd.sendto("CONNREQ".encode(), (ip, port))
        ack, _ = client_sd.recvfrom(1024)
        if ack != b"ACK":
            responses.connectionRefused(err)
        # Print success message
        print("-------------------------------------------------------------")
        print(f"A UDP client connected to server {ip}, port {port}")
        print("-------------------------------------------------------------")
    except Exception as err:
        responses.err(err)

    sendData(client_sd, ip, port, file)

def handleClientData(packetNum, server, client):
    print(f"Received packet {packetNum}")

    server.sendto(str(packetNum).encode(), client)