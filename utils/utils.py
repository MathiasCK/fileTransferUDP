from . import header
import random

def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")

def sendFINPacket(client_sd, server, seq_num, ex_ack):
    packet = header.create_packet(seq_num, ex_ack, 2, 0, b'')
    client_sd.sendto(packet, server)

def createAndSendPacket(sender, receiver, ex_packetNum, seq_num, flag, window, data):
    # See header.create_packet()
    packet = header.create_packet(seq_num, ex_packetNum, flag, window, data)
    # Send packet from sender to receiver
    sender.sendto(packet, receiver)

def checkReliabilityMatch(rel1, rel2):
    return rel1 == rel2

def handleSkipAck():
    return random.randint(10, 20)