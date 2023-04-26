import socket
from utils import responses, header, utils

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

    with open(file_path, 'rb') as file:

        if reliability is not None:
            if reliability == 'SAW':
                return stop_and_wait(client_sd, ip, port, file)
            
        return sendData(client_sd, ip, port, file)

def connectClient(client_sd, ip, port):
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

    