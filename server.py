import socket
from utils import utils, arguments, header

# Code execution starts here
def Main():
    # See utils -> arguments.checkServerOpts()
    bind, port, trigger, reliability = arguments.checkServerOpts()
    # Set up server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind server socket
    server.bind((bind, port))

    # Print success message
    print("---------------------------------------------")
    print(f"A UDP server is listening on port {str(port)}")
    print("---------------------------------------------")

    # Keep track of expected incomming packet
    ex_packetNum = 0
    # Keep track of expected sequence number
    expected_seq_num = 0
    # Received buffer
    receive_buffer = {}

    # Write incomming image to safi-recv.jpg
    with open('safi-recv.jpg', 'wb') as f:
        while True:
            # Receive data from client
            data, client = server.recvfrom(1472)
            # Decode data headers (first 12 bytes)
            headers = data[:12]
            # Sequence number, ack, flags & window size
            # See -> header.parse_header()
            seq, ack, flags, win = header.parse_header (headers)
            # Parse header flags
            synFlag, ackFlag, finFlag = header.parse_flags(flags)

            # Data transfer is finished (fin flag == 0010)
            if finFlag == 2:
                # Break execution
                break
            
            # Initialize connection (sender sends SYN flag on 1000)
            if synFlag == 8:
                # Server responds with SYN/ACK flag (1100)
                packet = header.create_packet(0, 0, 12, 0, b'')
                # Send ack to client
                server.sendto(packet, client)
                continue
            
            # SR connection
            if win == 5 and flags == 0:
                # Add received data to buffer
                receive_buffer[seq] = data
                print(f"Received packet {ack}")
                # Send ack to client
                server.sendto(str(ack).encode(), client)

                while expected_seq_num in receive_buffer:
                    # Write received data to image file
                    f.write(receive_buffer[expected_seq_num])
                    # Delete buffer
                    del receive_buffer[expected_seq_num]
                    # Update seq value
                    expected_seq_num += 1

            # GBN connection 
            if win == 5:
                # Write received data to image file
                f.write(data)
                print(f"Received packet {ack}")
                # Send ack to client
                server.sendto(str(ack).encode(), client)
                # Update expected packet value
                expected_seq_num += 1
                continue

            # Check if packet is not the expected packet
            if seq != ex_packetNum:
                # See -> utils.invalidPacket()
                utils.invalidPacket(seq, 'Received out of order')
                # Continue execution
                continue
            
            # If no ack flag is provided continue (force sender to resend packet)
            if ackFlag != 4:
                continue;
            
            # Write data to image
            f.write(data)
            print(f"Received packet {ack}")
            # Send ack to client
            server.sendto(str(ack).encode(), client)
            
            # Update expected packet value
            ex_packetNum += 1
            
        # Create empty ack packet
        packet = header.create_packet(ex_packetNum, seq, 4, 0, b'')
        # Send empty ack with ack flag to client
        server.sendto(packet, client)
        # Close server-client connection
        server.close()

if __name__ == '__main__':
    Main()
