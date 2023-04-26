from . import header
import socket

def validateCheckSum(payload, checksum):
    return checksum == sum(payload) % 256

def invalidPacket(packet_num, msg):
    print(f"Dropping packet {packet_num} - {msg}")

def stop_and_wait(client_sd, seq_num, ex_ack, file, ip, port):
    client_sd.settimeout(0.5)

    while True:
        # Read next chunk from file
        chunk = file.read(1460)

        packet = header.create_packet(seq_num, ex_ack, 4, 0, chunk)

        client_sd.sendto(packet, (ip, port))

        try:
            ack, _ = client_sd.recvfrom(1472)

            ack_num = int(ack.decode())

            if ack_num == ex_ack:
                print(f"Packet {seq_num} sent")
                seq_num += 1
                ex_ack += 1
            elif ex_ack == seq_num:
                print(f"Packet {ex_ack} - Duplicate ack received")
                continue
        except socket.timeout:
            print(f"Packet {seq_num} timed out - Resending packet")
            continue

        if not chunk:
            packet = header.create_packet(seq_num, ex_ack, 2, 0, chunk)
            client_sd.sendto(packet, (ip, port))
            break
        
    client_sd.close()


def GBN():
    return

def SR():
    return