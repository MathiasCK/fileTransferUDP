import socket
from utils import header, utils, responses
from collections import deque

def stop_and_wait(client_sd, server, file):

    seq_num = 0
    ex_ack = 0

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        utils.createAndSendPacket(client_sd, server, seq_num, ex_ack, 4, 0, chunk)

        try:
            client_sd.settimeout(0.5)
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
            print(f"Packet {seq_num} timed out (stop_and_wait) - resending packet")
            continue

        if not chunk:
            utils.sendFINPacket(client_sd, server, seq_num, ex_ack)
            break
        
    client_sd.close()

def GBN(client_sd, server, file):
    window_size = 5
    base = 0
    next_seq_num = 0
    unacknowledged_packets = {}

    while True:
        if next_seq_num < base + window_size:
            payload = file.read(1460)

            if not payload:
                break

            utils.createAndSendPacket(client_sd, server, next_seq_num, next_seq_num, 4, 5, payload)

            print(f"Packet {next_seq_num} sent")
            
            unacknowledged_packets[next_seq_num] = payload
            next_seq_num += 1

        try:
            client_sd.settimeout(0.5)
            ack, _ = client_sd.recvfrom(1024)
            ack_seq_num = int(ack.decode())

            if ack_seq_num in unacknowledged_packets:
                base = ack_seq_num + 1
                del unacknowledged_packets[ack_seq_num]

        except socket.timeout:
            for seq_num, payload in unacknowledged_packets.items():
                print(f"Packet {seq_num} timed out (GBN) - resending packet")
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)

                print(f"Packet {seq_num} sent")
   
    utils.sendFINPacket(client_sd, server, next_seq_num, next_seq_num)

def SR(client_sd, server, file):
    window_size = 5
    base = 0
    next_seq_num = 0
    unacknowledged_packets = {}
    buffer = deque()
    while True:
        if len(buffer) < window_size:
            payload = file.read(1460)
            if payload:
                buffer.append(payload)
            else:
                break
        if next_seq_num < base + window_size and buffer:
            payload = buffer.popleft()

            utils.createAndSendPacket(client_sd, server, next_seq_num, next_seq_num, 0, 5, payload)

            print(f"Packet {next_seq_num} sent")

            unacknowledged_packets[next_seq_num] = payload
            next_seq_num += 1

        try:
            client_sd.settimeout(0.5)
            ack, _ = client_sd.recvfrom(1024)
            ack_seq_num = int(ack.decode())

            if ack_seq_num in unacknowledged_packets:
                del unacknowledged_packets[ack_seq_num]
                base = min(unacknowledged_packets) if unacknowledged_packets else ack_seq_num + 1

        except socket.timeout:
            print(f"Packet {next_seq_num} timed out (SR) - resending packet")
            for seq_num, payload in unacknowledged_packets.items():
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)

                print(f"Packet {seq_num} sent")

    utils.sendFINPacket(client_sd, server, next_seq_num, next_seq_num)

def sendData(client_sd, server, file):

    seq_num = 0
    ex_ack = 0

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        utils.createAndSendPacket(client_sd, server, seq_num, ex_ack, 4, 0, chunk)

        ack_received = False

        while not ack_received:
            try:
                client_sd.settimeout(0.5)
                ack, _ = client_sd.recvfrom(1472)

                if int(ack.decode()) == seq_num:
                    ack_received = True
                    print(f"Packet {seq_num} sent")
                    seq_num += 1
                    ex_ack += 1

            except socket.timeout:
                print(f"Packet {seq_num} timed out - Resending packet")
                utils.createAndSendPacket(client_sd, server, seq_num, ex_ack, 4, 0, chunk)

        if not chunk:
            utils.sendFINPacket(client_sd, server, seq_num, ex_ack)
            break
        
    client_sd.close()

def handleReliability(client_sd, server, file_path, reliability):

    with open(file_path, 'rb') as file:

        if reliability == 'SAW':
            return stop_and_wait(client_sd, server, file)
        if reliability == 'GBN':
            return GBN(client_sd, server, file)
        if reliability == 'SR':
            return SR(client_sd, server, file)
            
        return sendData(client_sd, server, file)

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

def handleSRData(receive_buffer, seq, data, ack, client, server, f, expected_seq_num):
    # Add received data to buffer
    receive_buffer[seq] = data
    print(f"Received packet {ack}")
    # Send ack to client
    server.sendto(str(ack).encode(), client)

    while expected_seq_num in receive_buffer:
        # Write received data to image file
        f.write(receive_buffer[expected_seq_num])
        # Delete buffer
        del receive_buffer[expected_seq_num]

def initializeClientConnection(server, client, data, reliability):
    # Decode data
    data = data[12:].decode()
    # See -> utils.checkReliabilityMatch()
    if not utils.checkReliabilityMatch(str(data), str(reliability)):
        # Format message
        msg = f'Server reliability "{reliability}" does not match client reliability "{data}"'
        # See utils.createAndSendPacket()
        utils.createAndSendPacket(server, client, 0, 0, 1, 0, msg.encode())
        # See -> responses.syntaxError()
        responses.syntaxError(msg)
    
    # Send packet with SYN/ACK flag to client
    # See utils.createAndSendPacket()
    utils.createAndSendPacket(server, client, 0, 0, 12, 0, b'')