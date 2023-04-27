from . import header
import random

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