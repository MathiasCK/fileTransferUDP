import socket
from utils import responses, header, utils
import hashlib

def stop_and_wait(client_sd, ip, port, file):

    seq_num = 0
    ex_ack = 0

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        packet = header.create_packet(seq_num, ex_ack, 4, 0, chunk)

        client_sd.sendto(packet, (ip, port))

        try:
            ack, _ = client_sd.recvfrom(1472)

            ack_num = int(ack.decode())

            if ack_num == ex_ack:
                print(f"Packet {seq_num} sent")
                seq_num += 1
                ex_ack += 1
            elif ex_ack == seq_num:
                print(f"Packet {ex_ack} - Duplicate ack received")
                continue
        except socket.timeout:
            print(f"Packet {seq_num} timed - Stop and wait")
            client_sd.settimeout(0.5)
            continue

        if not chunk:
            utils.sendFINPacket(client_sd, ip, port, seq_num, ex_ack)
            break
        
    client_sd.close()

def make_packet(seq_num, payload):
    checksum = hashlib.md5(payload).hexdigest()
    header = f"{seq_num}|{checksum}"
    return header.encode() + payload

def send_packet(sock, addr, seq_num, payload):
    packet = make_packet(seq_num, payload)
    sock.sendto(packet, addr)

def recv_ack(sock):
    data, addr = sock.recvfrom(1024)
    return int(data.decode()[3:])

def GBN(client_sd, ip, port, file):
    window_size = 5
    base = 0
    next_seq_num = 0
    unacknowledged_packets = {}
    file_data = []

    while True:
        if next_seq_num < base + window_size:
            payload = file.read(1460)

            if not payload:
                break

            send_packet(client_sd, (ip, port), next_seq_num, payload)
            print(next_seq_num)
            unacknowledged_packets[next_seq_num] = payload
            next_seq_num += 1

        try:
            ack_seq_num = recv_ack(client_sd)

            if ack_seq_num in unacknowledged_packets:
                base = ack_seq_num + 1
                del unacknowledged_packets[ack_seq_num]

        except socket.timeout:
            for seq_num, payload in unacknowledged_packets.items():
                send_packet(client_sd, (ip, port), seq_num, payload)

    send_packet(client_sd, (ip, port), -1, b'')

def sendData(client_sd, ip, port, file):

    seq_num = 0
    ex_ack = 0

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        packet = header.create_packet(seq_num, ex_ack, 4, 0, chunk)
        
        client_sd.sendto(packet, (ip, port))

        ack_received = False

        while not ack_received:
            try:
                ack, _ = client_sd.recvfrom(1472)

                if int(ack.decode()) == seq_num:
                    ack_received = True
                    print(f"Packet {seq_num} sent")
                    seq_num += 1
                    ex_ack += 1

            except socket.timeout:
                print(f"Packet {seq_num} timed out - Resending packet")
                client_sd.sendto(packet.encode(), (ip, port))

        if not chunk:
            utils.sendFINPacket(client_sd, ip, port, seq_num, ex_ack)
            break
        
    client_sd.close()

def handleClientData(client_sd, ip, port, file_path, reliability):

    print("-------------------------------------------------------------")
    print(f"A UDP client connected to server {ip}, port {port}")
    print("-------------------------------------------------------------")

    with open(file_path, 'rb') as file:

        if reliability is not None:
            if reliability == 'SAW':
                return stop_and_wait(client_sd, ip, port, file)
            if reliability == 'GBN':
                return GBN(client_sd, ip, port, file)
            
        return sendData(client_sd, ip, port, file)


    