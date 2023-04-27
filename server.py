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

            # Data transfer is finished (fin flag == 0010)
            if flags == 2:
                # Break execution
                break

            # Initialize connection (sender sends SYN flag on 1000)
            if flags == 8:
                # See -> data_handlers.initializeClientConnection()
                data_handlers.initializeClientConnection(server, client, data, reliability)
                continue

            # Skip ack if the skipack flag is provided
            # Explanation: The trigger value wil skip every "trigger"th incomming sequence
            if trigger is not None and seq % trigger == 0 and seq != 0 and i != seq:
                i = seq
                continue

            # Check if packet is not the expected packet
            if seq != expected_seq_num:
                # See -> utils.invalidPacket()
                utils.invalidPacket(seq, 'Received out of order')
                # Continue execution
                continue

            # SR connection
            if reliability == "SR":
                # See data_handlers.handleSRData()
                data_handlers.handleSRData(receive_buffer, seq, data, ack, client, server, f, expected_seq_num)
            # GBN connection 
            elif reliability == "GBN":
                # See -> data_handlers.handleGBNData()
                data_handlers.handleGBNData(client, server, ack, f, data)
            else:
                # See -> data_handlers.handleClientData()
                data_handlers.handleClientData(client, server, ack, data, f)
            
            # Update expected packet value
            expected_seq_num += 1
        
        # See utils.createAndSendPacket()
        utils.createAndSendPacket(server, client, seq, expected_seq_num, 4, 0, b'')
        # Close server-client connection
        server.close()

if __name__ == '__main__':
    Main()
