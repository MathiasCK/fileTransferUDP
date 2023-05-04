import socket
from utils import utils, responses
from collections import deque
import time
import os

# Handle client data with SAW reliability
# @client_sd -> client socket
# @server -> server socket
# @file -> file for dispatch
# @trigger -> trigger value (-t flag) - Default None
def stop_and_wait(client_sd, server, file, trigger):
    # Default starting sequence number
    sequence_number = 0
    # Default starting ack
    expected_ack = 0
    # Default timeout
    timeout = 0.5
    # All rtt values received
    rtt_values = []
    # Time since start of data transfer
    start_time = time.time()
    # Total size of file
    file_size = os.fstat(file.fileno()).st_size

    while True:
        # Read next chunk from file
        chunk = file.read(1460)
        # See -> utils.sendData()
        utils.sendData(client_sd, server, sequence_number, expected_ack, 4, 0, chunk, trigger)

        try:
            # Set default timeout
            client_sd.settimeout(timeout)
            # Receive data (ack) from client
            ack, _ = client_sd.recvfrom(1472)
            # Decode ack from data
            ack_num = int(ack.decode())
            # If ack is the same as the expected ack
            if ack_num == expected_ack:
                print(f"Packet {sequence_number} sent")
                # Update sequence number and ack -> send next packet
                sequence_number += 1
                expected_ack += 1
                # Calculate new timeout
                # See -> utils.calculateNewTimeout()
                # timeout = utilscalculateNewTimeout(start_time, rtt_values)
            # If expected ack is the same as sequence_number (duplicate happened) continue execution
            elif expected_ack == sequence_number:
                print(f"Packet {expected_ack} - Duplicate ack received")
                continue
            # If a timeout happens (packet was not sent) - continue execution
        except socket.timeout:
            print(f"Packet {sequence_number} timed out (stop_and_wait) - resending packet")
            continue
        # If no chunk -> packet transfer is finished
        if not chunk:
            # See -> utils.calculateThroughput()
            utils.calculateThroughput(file_size, start_time)
            # See -> utils.sendFINPacket()
            utils.sendFINPacket(client_sd, server, sequence_number, expected_ack)
            break
    # Close client connection
    client_sd.close()

# Handle client data with GBN reliability
# @client_sd -> client socket
# @server -> server socket
# @file -> file for dispatch
# @trigger -> trigger value (-t flag) - Default None
def GBN(client_sd, server, file, trigger):
    # Default window size
    window_size = 5
    # Starting window size
    window_size_start = 0
    # Default starting sequence number
    sequence_number = 0
    # Default timeout
    timeout = 0.5
    # Packets where no ack is received
    unacked_packets = {}
    # All rtt values received
    rtt_values = []
    # Time since start of data transfer
    start_time = time.time()
    # Append start time to rtt_values
    rtt_values.append(start_time)
    # Total size of file
    file_size = os.fstat(file.fileno()).st_size

    while True:
        # As long as the sequence number is less than starting window size + the total window size (window size is big enough)
        if sequence_number < window_size_start + window_size:
            # Read the file
            payload = file.read(1460)

            # Break execution if no payload (data transfer complete)
            if not payload:
                break
            
            # See -> utils.sendData()
            utils.sendData(client_sd, server, sequence_number, sequence_number, 4, 5, payload, trigger)

            print(f"Packet {sequence_number} sent")
            
            # Add packet to unack packet -> packet is not yet acked
            unacked_packets[sequence_number] = payload
            # Update sequence number
            sequence_number += 1

        try:
            # Set default timeout
            client_sd.settimeout(timeout)
            # Receive data (ack) from client
            ack, _ = client_sd.recvfrom(1472)
            # Decode ack from data
            ack_num = int(ack.decode())
            # If the ack is found in unacked_packets
            if ack_num in unacked_packets:
                # Update the start size of the window
                window_size_start = ack_num + 1
                # Delete ack from unacked_packets -> (mark packet as acked)
                del unacked_packets[ack_num]
                # Calculate new timeout
                # See -> utils.calculateNewTimeoutAndPop()
                # timeout = utilscalculateNewTimeoutAndPop(rtt_values)
        # If a timeout happens (packet was not sent)
        except socket.timeout:
            # Loop and re-send all unacked packets
            for seq_num, payload in unacked_packets.items():
                print(f"Packet {seq_num} timed out (GBN) - resending packet")
                # See utils.createAndSendPacket()
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)
    
    # See -> utils.calculateThroughput()
    utils.calculateThroughput(file_size, start_time)
    # See -> utils.sendFINPacket()
    utils.sendFINPacket(client_sd, server, sequence_number, sequence_number)
    # Close client connection
    client_sd.close()

# Handle client data with SR reliability
# @client_sd -> client socket
# @server -> server socket
# @file -> file for dispatch
# @trigger -> trigger value (-t flag) - Default None
def SR(client_sd, server, file, trigger):
    # Default window size
    window_size = 5
    # Starting window size
    window_size_start = 0
    # Default starting sequence number
    sequence_number = 0
    # Default timeout
    timeout = 0.5
    # Packets where no ack is received
    unacked_packets = {}
    # Buffer
    buffer = deque()
    # All rtt values received
    rtt_values = []
    # Time since start of data transfer
    start_time = time.time()
    # Append start time to rtt_values
    rtt_values.append(start_time)

    while True:
        # As long as the buffer is less than the window size
        if len(buffer) < window_size:
            # Read data from file
            payload = file.read(1460)
            # Break execution if no payload (data transfer complete)
            if not payload:
                break
            # Add the payload to the buffer
            buffer.append(payload)
        
        # As long as the sequence number is less than starting window size + the total window size (window size is big enough) and buffer is not None
        if sequence_number < window_size_start + window_size and buffer:
            # Get latest payload from buffer
            payload = buffer.popleft()
            # See -> utils.sendData()
            utils.sendData(client_sd, server, sequence_number, sequence_number, 0, 5, payload, trigger)

            print(f"Packet {sequence_number} sent")

            # Add packet to unack packet -> packet is not yet acked
            unacked_packets[sequence_number] = payload
            # Update sequence number
            sequence_number += 1

        try:
            # Set default timeout
            client_sd.settimeout(timeout)
            # Receive data (ack) from client
            ack, _ = client_sd.recvfrom(1472)
            # Decode ack from data
            ack_num = int(ack.decode())
            # If the ack is found in unacked_packets
            if ack_num in unacked_packets:
                # Delete ack from unacked_packets -> (mark packet as acked)
                del unacked_packets[ack_num]
                # If there is any more unacked packets
                if unacked_packets:
                    # Set the beginning window size to the smallest unacked packet
                    window_size_start = min(unacked_packets)
                else:
                    # Update window size by 1
                    window_size_start = ack_num + 1
                # Calculate new timeout
                # See -> utils.calculateNewTimeoutAndPop()
                # timeout = utilscalculateNewTimeoutAndPop(rtt_values)
        # If a timeout happens (packet was not sent)
        except socket.timeout:
            print(f"Packet {sequence_number} timed out (SR) - resending packet")
            # Loop and re-send all unacked packets
            for seq_num, payload in unacked_packets.items():
                # See -> utils.createAndSendPacket()
                utils.createAndSendPacket(client_sd, server, seq_num, seq_num, 4, 5, payload)
    # See -> utils.sendFINPacket()
    utils.sendFINPacket(client_sd, server, sequence_number, sequence_number)
    # Close client connection
    client_sd.close()

# Handle client data with default reliability
# @client_sd -> client socket
# @server -> server socket
# @file -> file for dispatch
# @trigger -> trigger value (-t flag) - Default None
def handleData(client_sd, server, file, trigger):
    # Default starting sequence number
    sequence_number = 0
    # Default starting ack
    expected_ack = 0
    # Default timeout
    timeout = 0.5
    # All rtt values received
    rtt_values = []
    # Time since start of data transfer
    start_time = time.time()

    while True:
        # Read next chunk from file
        chunk = file.read(1460)
        # See -> utils.sendData()
        utils.sendData(client_sd, server, sequence_number, expected_ack, 4, 0, chunk, trigger)

        # Boolean value (ack not yet received)
        ack_received = False
        while not ack_received:
            try:
                # Set default timeout
                client_sd.settimeout(timeout)
                # Receive data (ack) from client
                ack, _ = client_sd.recvfrom(1472)
                # Decode ack from data
                ack_num = int(ack.decode())
                # If ack is the same as sequence number
                if ack_num == sequence_number:
                    # Update boolean
                    ack_received = True
                    print(f"Packet {sequence_number} sent")
                    # Update sequence number and ack -> send next packet
                    sequence_number += 1
                    expected_ack += 1
                    # Calculate new timeout
                    # See -> utils.calculateNewTimeout()
                    # timeout = utilscalculateNewTimeout(start_time, rtt_values)
            # If a timeout happens (packet was not sent)
            except socket.timeout:
                print(f"Packet {sequence_number} timed out - Resending packet")
                # Send packet again
                # See -> utils.createAndSendPacket()
                utils.createAndSendPacket(client_sd, server, sequence_number, expected_ack, 4, 0, chunk)
        # If no chunk -> packet transfer is finished
        if not chunk:
            # See -> utils.sendFINPacket()
            utils.sendFINPacket(client_sd, server, sequence_number, expected_ack)
            break
    # Close client connection
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
    data = data.decode()
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