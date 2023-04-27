import socket
from utils import utils, responses
from collections import deque
import time

def stop_and_wait(client_sd, server, file, trigger):
    seq_num = 0
    ex_ack = 0
    timeout = 0.5

    rtt_values = []
    start_time = time.time()

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        utils.sendData(client_sd, server, seq_num, ex_ack, 4, 0, chunk, trigger)

        try:
            client_sd.settimeout(timeout)
            ack, _ = client_sd.recvfrom(1472)

            ack_num = int(ack.decode())

            if ack_num == ex_ack:
                print(f"Packet {seq_num} sent")
                seq_num += 1
                ex_ack += 1

                rtt = time.time() - start_time
                rtt_values.append(rtt)
                timeout = sum(rtt_values) / len(rtt_values) * 4
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

def GBN(client_sd, server, file, trigger):
    window_size = 5
    base = 0
    next_seq_num = 0
    timeout = 0.5

    rtt_values = []
    unacknowledged_packets = {}

    start_time = time.time()
    rtt_values.append(start_time)

    while True:
        if next_seq_num < base + window_size:
            payload = file.read(1460)

            if not payload:
                break

            utils.sendData(client_sd, server, next_seq_num, next_seq_num, 4, 5, payload, trigger)

            print(f"Packet {next_seq_num} sent")
            
            unacknowledged_packets[next_seq_num] = payload
            next_seq_num += 1

        try:
            client_sd.settimeout(timeout)
            ack, _ = client_sd.recvfrom(1024)
            ack_seq_num = int(ack.decode())

            if ack_seq_num in unacknowledged_packets:
                end_time = time.time()
                rtt = end_time - rtt_values.pop(0)
                if len(rtt_values) > 10:
                    rtt_values.pop(0)
                rtt_values.append(rtt)
                timeout = sum(rtt_values) / len(rtt_values) * 4

                base = ack_seq_num + 1
                del unacknowledged_packets[ack_seq_num]

        except socket.timeout:
            for seq_num, payload in unacknowledged_packets.items():
                print(f"Packet {seq_num} timed out (GBN) - resending packet")
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)

                print(f"Packet {seq_num} sent")
   
    utils.sendFINPacket(client_sd, server, next_seq_num, next_seq_num)

def SR(client_sd, server, file, trigger):
    window_size = 5
    base = 0
    next_seq_num = 0
    timeout = 0.5
    unacknowledged_packets = {}
    buffer = deque()
    rtt_values = []

    start_time = time.time()
    rtt_values.append(start_time)

    while True:
        if len(buffer) < window_size:
            payload = file.read(1460)
            if payload:
                buffer.append(payload)
            else:
                break
        if next_seq_num < base + window_size and buffer:
            payload = buffer.popleft()

            utils.sendData(client_sd, server, next_seq_num, next_seq_num, 0, 5, payload, trigger)

            print(f"Packet {next_seq_num} sent")

            unacknowledged_packets[next_seq_num] = payload
            next_seq_num += 1

        try:
            client_sd.settimeout(timeout)
            ack, _ = client_sd.recvfrom(1024)
            ack_seq_num = int(ack.decode())

            if ack_seq_num in unacknowledged_packets:
                end_time = time.time()
                rtt = end_time - rtt_values.pop(0)
                if len(rtt_values) > 10:
                    rtt_values.pop(0)
                rtt_values.append(rtt)
                timeout = sum(rtt_values) / len(rtt_values) * 4

                del unacknowledged_packets[ack_seq_num]
                base = min(unacknowledged_packets) if unacknowledged_packets else ack_seq_num + 1

        except socket.timeout:
            print(f"Packet {next_seq_num} timed out (SR) - resending packet")
            for seq_num, payload in unacknowledged_packets.items():
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)

                print(f"Packet {seq_num} sent")

    utils.sendFINPacket(client_sd, server, next_seq_num, next_seq_num)

def handleData(client_sd, server, file, trigger):
    seq_num = 0
    ex_ack = 0
    timeout = 0.5

    rtt_values = []
    start_time = time.time()

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        utils.sendData(client_sd, server, seq_num, ex_ack, 4, 0, chunk, trigger)
        
        ack_received = False

        while not ack_received:
            try:
                client_sd.settimeout(timeout)
                ack, _ = client_sd.recvfrom(1472)

                if int(ack.decode()) == seq_num:
                    ack_received = True
                    print(f"Packet {seq_num} sent")
                    seq_num += 1
                    ex_ack += 1

                    rtt = time.time() - start_time
                    rtt_values.append(rtt)
                    timeout = sum(rtt_values) / len(rtt_values) * 4

            except socket.timeout:
                print(f"Packet {seq_num} timed out - Resending packet")
                utils.createAndSendPacket(client_sd, server, seq_num, ex_ack, 4, 0, chunk)

        if not chunk:
            utils.sendFINPacket(client_sd, server, seq_num, ex_ack)
            break
        
    client_sd.close()

# Handle -r flag (if provided) from client
# @client_sd -> client socket
# @server -> server socket
# @file_path -> value provided with -f flag (if provided) - Default ./Photo.jpg
# @trigger -> value provided with -t flag (if provided) - Default None
# @reliability -> value provided with -r flag (if provided) - Default None
def handleReliability(client_sd, server, file_path, trigger, reliability):
    # Open file
    with open(file_path, 'rb') as file:
        # Check reliability match
        if reliability == 'SAW':
            # See -> stop_and_wait()
            return stop_and_wait(client_sd, server, file, trigger)
        if reliability == 'GBN':
            # See -> GBN()
            return GBN(client_sd, server, file, trigger)
        if reliability == 'SR':
            # See -> SR()
            return SR(client_sd, server, file, trigger)
        # See -> handleData()
        return handleData(client_sd, server, file, trigger)

# Handle incomming client data if -r SR flag is provided
# @client_sd -> client socket
# @server -> server socket
# @ack -> ack received from client
# @data -> data received from client
# @file -> output file from server
# @receive_buffer -> object of buffer data received from client
# @seq -> sequence number received from client
# @expected_seq_num -> expected sequence number of server
def handleSRData(client, server, ack, data, file, receive_buffer, seq, expected_seq_num):
    # Add received data to buffer
    receive_buffer[seq] = data
    print(f"Received packet {ack}")
    # Encode ack and send to client
    server.sendto(str(ack).encode(), client)

    # As long as the expected sequence number is in the receive buffer - (as long as the data received has not yet been acked)
    while expected_seq_num in receive_buffer:
        # Write received data to image file
        file.write(receive_buffer[expected_seq_num])
        # Delete buffer (send ack)
        del receive_buffer[expected_seq_num]

# Handle incomming client data
# @client -> client socket
# @server -> server socket
# @ack -> ack received from client
# @data -> data received from client
# @file -> output file from server
def handleClientData(client, server, ack, data, file):
    # Write data to image
    file.write(data)
    print(f"Received packet {ack}")
    # Encode ack and send to client
    server.sendto(str(ack).encode(), client)

# Validate incomming client data upon receiving connection request
# @server -> server socket
# @client -> client socket
# @data -> data received from client
# @reliability -> client reliability
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
    
    # Send empty packet with SYN/ACK flag (1100 = 12) to client indicating connection was successful
    # See utils.createAndSendPacket()
    utils.createAndSendPacket(server, client, 0, 0, 12, 0, b'')