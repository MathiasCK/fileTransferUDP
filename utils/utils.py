def createPacket(sequence_number, data):
    return f"{sequence_number}:{sum(data) % 256}:{data}"

def decodePacket(data):
    packet = data.decode().split(':')
    return int(packet[0]), int(packet[1]), packet[2]

def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")