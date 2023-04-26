from . import header

def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")

def sendFINPacket(client_sd, ip, port, seq_num, ex_ack):
    packet = header.create_packet(seq_num, ex_ack, 2, 0, b'')
    client_sd.sendto(packet, (ip, port))