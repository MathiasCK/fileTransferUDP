import socket
from utils import utils, arguments, header, data_handlers

# Code execution starts here
def Main():
    # See utils -> arguments.checkServerOpts()
    bind, port, trigger, reliability, file = arguments.checkServerOpts()
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
    # Default receiving image file
    img = 'safi-recv.jpg'
    # Handle -f flag
    if file is not None:
        img = file
    # Handle -t flag
    if trigger == "skipack":
        # Global incomming seq counter
        i = 0
        # See utils.handleSkipAck()
        trigger = utils.handleSkipAck()
        print(f"Trigger will skip ack for every {trigger}th packet")

    # Write incomming image to safi-recv.jpg
    with open(img, 'wb') as f:
        while True:
            # Receive data from client
            data, client = server.recvfrom(1472)
            # Decode data headers (first 12 bytes)
            headers = data[:12]
            # Sequence number, ack, flags & window size
            # See -> header.parse_header()
            seq, ack, flags, win = header.parse_header (headers)

            # Skip ack if the skipack flag is provided
            # Explanation: The trigger value wil skip every "trigger"th incomming sequence
            if trigger is not None and seq % trigger == 0 and seq != 0 and i != seq:
                i = seq
                continue
            # Parse header flags
            synFlag, ackFlag, finFlag = header.parse_flags(flags)

            # Data transfer is finished (fin flag == 0010)
            if finFlag == 2:
                # Break execution
                break
            
            # Initialize connection (sender sends SYN flag on 1000)
            if synFlag == 8:
                # See -> data_handlers.initializeClientConnection()
                data_handlers.initializeClientConnection(server, client, data, reliability)
                continue
                    
            # SR connection
            if reliability == "SR":
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
                
                continue

            # GBN connection 
            if reliability == "GBN":
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
        
        # See utils.createAndSendPacket()
        utils.createAndSendPacket(server, client, seq, ex_packetNum, 4, 0, b'')
        # Close server-client connection
        server.close()

if __name__ == '__main__':
    Main()
