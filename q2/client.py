import socket
import sys
import os
import time
from protocol import PKT_ACK, build_info, build_data, build_checksum, parse_ack

CHUNK_SIZE = 1024
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 6730

def send_file(filepath: str):
    filename = os.path.basename(filepath)

    with open(filepath, 'rb') as f:
        file_bytes = f.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # PKT_INFO _____________________________________
    sock.sendto(build_info(filename, len(file_bytes)), (SERVER_HOST, SERVER_PORT))
    print(f"[CLIENT] Sending '{filename}' ({len(file_bytes)} bytes)")

    # PKT_DATA _____________________________________
    sock.settimeout(0.5) # changes the socket to non-blocking mode with a timeout of 0.5 seconds.

    chunk_number = 0
    for i in range(0, len(file_bytes), CHUNK_SIZE):
        chunk = file_bytes[i : i + CHUNK_SIZE]
        data_pkt = build_data(chunk_number, chunk)
        ack_received = False
        
        # stop-and-Wait strategy: avoids sending the next chunk until the ACK for the current chunk is received
        while not ack_received:
            sock.sendto(data_pkt, (SERVER_HOST, SERVER_PORT))
            
            try:
                ack_data, _ = sock.recvfrom(1024) # waits for the ACK response from the server, with a timeout of 0.5s
                if ack_data[0] == PKT_ACK: 
                    ack_num = parse_ack(ack_data)
                    
                    # checks if the ACK received corresponds to the chunk just sent
                    if ack_num == chunk_number:
                        ack_received = True
                        
            except socket.timeout:
                # if timeout reaches, it means the ACK was not received, so it will resend the same chunk
                print(f"[CLIENT] Timeout no chunk {chunk_number}. Reenviando...")

        chunk_number += 1

    sock.settimeout(None) 
    print(f"[CLIENT] {chunk_number} chunks sent")
        

    print(f"[CLIENT] {chunk_number} chunks sent")

    # PKT_CHECKSUM _________________________________
    sock.sendto(build_checksum(file_bytes), (SERVER_HOST, SERVER_PORT))
    print(f"[CLIENT] Checksum sent. Transfer complete!")

    sock.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"[ERROR] File '{filepath}' not found.")
        sys.exit(1)

    send_file(filepath)

if __name__ == "__main__":
    main()