def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")

def GBN():
    return

def SR():
    return