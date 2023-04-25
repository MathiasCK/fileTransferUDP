import socket
from utils import utils, responses

def sendData(client_sd, ip, port):
    sequence_number = 0
    sent_data = ['This', 'is', 'only', 'test', 'data']

    for data in sent_data:
        packet = utils.createPacket(sequence_number, data)

        client_sd.sendto(packet.encode(), (ip, port))

        ack_received = False
        while not ack_received:
            try:
                client_sd.settimeout(1)
                data, _ = client_sd.recvfrom(1024)
                if int(data.decode()) == sequence_number:
                    ack_received = True
            except socket.timeout:
                print(f"Packet {sequence_number} timed out. Resending packet.")
                client_sd.sendto(packet.encode(), (ip, port))

        sequence_number += 1

    client_sd.sendto("ACK/BYE".encode(), (ip, port))
    

def connectClient(client_sd, ip, port):
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

    sendData(client_sd, ip, port)
