from . import header
import random
import time

# Checks if checksum received is valid
# @payload -> data received
# @checksum -> checksum received
# Returns boolean value
def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

# Prints invalid package message
# @packet_num -> packet number
# @msg -> custom message
def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")

# Sends empty packet indicating data transfer is complete with flag 2 (0010)
# @client_sd -> client socket
# @server -> server socket
# @seq_num -> final sequence number value
# @ex_ack -> final ack value
def sendFINPacket(client_sd, server, seq_num, ex_ack):
    # See -> header.create_packet()
    packet = header.create_packet(seq_num, ex_ack, 2, 0, b'')
    # Send packet from client to server
    client_sd.sendto(packet, server)

# Creating packet and sending packet
# @sender -> sending socket
# @receiver -> receiving socket
# @ack -> expected ack
# @seq_num -> expected sequence number
# @flag -> ACK flag bits
# @window -> window size
# @data -> data chunk to send
def createAndSendPacket(sender, receiver, ack, seq_num, flag, window, data):
    # See header.create_packet()
    packet = header.create_packet(seq_num, ack, flag, window, data)
    # Send packet from sender to receiver
    sender.sendto(packet, receiver)

# Checks if server -r flag matches client -r flag
# @rel1 -> server -r flag
# @rel2 -> client -r flag
# Returns boolean
def checkReliabilityMatch(rel1, rel2):
    return rel1 == rel2

# If -t skipack is provided by server, generate random number of acks to be skipped
# Returns a random number between 10 and 20
def handleSkipAck():
    return random.randint(10, 20)

# Send data from client to server
# @client -> client socket
# @server -> server socket
# @seq -> sequence number packet
# @ack -> expected ack
# @flag -> ACK flag bits
# @window -> window size
# @data -> data chunk to send
# @trigger -> if trigger is provided - Default None
def sendData(client, server, seq, ack, flag, window, data, trigger = None):
    # Packet probability to send is 100% by default
    packet_send_prob = 1

    # If trigger is provided
    if trigger is not None:
        # Packet probability to be sent is random
        packet_send_prob = random.random()
    
    # If packet send probability is larger than 0.1
    # This means it will be a 10% chance a packet will not be sent
    if packet_send_prob > 0.1:
        # See -> createAndSendPacket()
        createAndSendPacket(client, server, seq, ack, flag, window, data)

# Calculate new timeout after packet is received
# @start_time -> time since beginning of transfer
# @rtt_values -> array containing previous rtt values
# Returns new timeout value
def calculateNewTimeout(start_time, rtt_values):
    # Calculate last round trip time
    rtt = time.time() - start_time
    # Add last round trip time to array
    rtt_values.append(rtt)
    # New timeout value is calculated by the total values divided by the amount of values provided
    return sum(rtt_values) / len(rtt_values) * 4

# Calculate new timeout after packet is received for SR & GBN
# @rtt_values -> array containing previous rtt values
# Returns new timeout value
def calculateNewTimeoutAndPop(rtt_values):
    # Calculate time of received ack
    end_time = time.time()
    # Round trip time is calculating by taking the end time from the latest ack
    rtt = end_time - rtt_values.pop(0)
    # Remove latest rtt if the length is greater than 10
    if len(rtt_values) > 10:
        rtt_values.pop(0)
    # Append the newest rtt
    rtt_values.append(rtt)
    # New timeout value is calculated by the total values divided by the amount of values provided
    return sum(rtt_values) / len(rtt_values) * 4

# Calculate data throughput
# @file_size -> total size of file
# @start_time -> time since data transfer started
def calculateThroughput(file_size, start_time):
    # Stop timer
    end_time = time.time()
    # Calculate total time
    total_time = end_time - start_time
    total_time = "%.2f" % round(total_time, 2)
    # Calculate througput
    throughput = file_size / float(total_time)

    print(f"File size: {file_size} bytes")
    print(f"Total time: {total_time} seconds")
    print(f"Throughput: {int(throughput)} bytes/second")
