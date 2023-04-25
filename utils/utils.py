def createPacket(sequence_number, data):
    return f"{sequence_number}:{sum([ord(c) for c in data]) % 256}:{data}"