# Udp file transfer

## Introduction

This application provides reliable data delivery on top of UDP. The protocol will ensure that data is reliably delivered in-order without missing data or duplicates.

## Installation and usage

This is a tool that can operate in two different modes: client and server. By switching between these modes, the application can either transmit or receive data as required by the testing setup at hand.

To run the application in client mode run `python3 application.py -c`

#### Optional client arguments:

| Short flag | Long flag     | Description             | Default value | Required |
| ---------- | ------------- | ----------------------- | ------------- | -------- |
| -c         | --client      | Runs program as client  |               | true     |
| -I         | --serverip    | Server ip adress        | localhost     | false    |
| -p         | --port        | Server port             | 8080          | false    |
| -f         | --file        | File to transfer        | Photo.jpg     | false    |
| -t         | --trigger     | Trigger scenario        | None          | false    |
| -r         | --reliability | Run in realibility mode | None          | false    |

To run the application in server mode run `python3 application.py -s`

#### Optional server arguments:

| Short flag | Long flag     | Description             | Default value | Required |
| ---------- | ------------- | ----------------------- | ------------- | -------- |
| -s         | --server      | Runs program as server  |               | true     |
| -b         | --bind        | Server ip adress        | localhost     | false    |
| -p         | --port        | Server port             | 8080          | false    |
| -f         | --file        | File to receive data    | safi-recv.jpg | false    |
| -t         | --trigger     | Trigger scenario        | None          | false    |
| -r         | --reliability | Run in realibility mode | None          | false    |

## Reliability modes

Both the client and server can be ran in various reliability modes: stop_and_run (SAW), Go-Back-N (GBN) and Selective-Repeat (SR). Both server and client MUST use the same reliable_method.

#### Stop_and_run (SAW)

To run the application in SAW reliability mode run:

1. `python3 application.py -c -r SAW`
2. `python3 application.py -s -r SAW`

When SAW mode is active, the sender will send a packet, then wait for an ack confirming that packet. If an ack is arrived, it sends a new packet. If an ack does not arrive, it waits for timeout (fixed value: 500ms) and then resends the packet. If sender receives a duplicate ACK (ack of the last received sequence), it resends the packet.

#### Go-Back-N (GBN)

To run the application in GBN reliability mode run:

1. `python3 application.py -c -r GBN`
2. `python3 application.py -s -r GBN`

When running in GBN mode, the sender implements the Go-Back-N strategy using a fixed window size of 5 packets to transfer data. The sequence numbers represent packets, i.e. packet 1 is numbered 1, packet 2 is numbered 2 and so on. If no ACK packet is received within a given timeout (default value: 500ms), all packets that have not previously been acknowledged are assumed to be lost and they are retransmitted. A receiver passes on data in order and if packets arrive at the receiver in the wrong order, this indicates packet loss or reordering in the network. The DRTP receiver should in such cases not acknowledge anyting and may discard these packets.

#### Selective-Repeat (SR)

To run the application in SR reliability mode run:

1. `python3 application.py -c -r SR`
2. `python3 application.py -s -r SR`

When running in SR mode, rather than throwing away packets that arrive in the wrong order, the application will put the packets in the correct place in the recieve buffer

## Trigger scenarios

#### The client can trigger a packet-loss scenario by running the command below:

`python3 application.py -c -t loss`

This will result in a 10% probability any packet send by the client will not be received by the server. In such case the client will attempt to resend the packet untill it is received by the server

#### The server can skip an ack to trigger retransmission at the sender-side by running the command below:

`python3 application.py -s -t skipack`

This will result in the server will not send an ack to the server by dropping every x number of packets (where x is a random number between 10 and 20). This will force the client to attempt to resend the packet

## Running the App with Node and NPM

To run this app using Node and NPM, follow these steps:

1. Make sure you have Node.js and NPM installed on your system.
2. Run the command `npm install` to install all the dependencies required by the app.
3. Once the installation is complete, run any of the built-in commands listed in `package.json`
