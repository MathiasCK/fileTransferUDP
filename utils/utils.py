def createPacket(sequence_number, data):
    return f"{sequence_number}:{sum([ord(c) for c in data]) % 256}:{data}"

def decodePacket(data):
    packet = data.decode().split(':')
    return int(packet[0]), packet[1], packet[2]

def validateCheckSum(payload, checksum):
    rec_checksum = str(sum([ord(c) for c in payload]) % 256)
    return checksum == rec_checksum

def invalidPacket(packetNum, msg):
    print(f"Dropping packet: {packetNum} - {msg}")