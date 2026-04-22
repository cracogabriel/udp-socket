import socket
import os
from protocol import (PKT_INFO, PKT_DATA, PKT_CHECKSUM, build_ack, parse_info, parse_data, parse_checksum, compute_checksum)

HOST    = '0.0.0.0'
PORT    = 6730
STORAGE = 'server-storage'

def main():
    os.makedirs(STORAGE, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    transfers = {}  # { addr: { 'filename': ..., 'file_size': ..., 'chunks': {} } } -> this is a dictionary to keep track of ongoing transfers by sender address

    while True:
        data, addr = sock.recvfrom(2048)
        pkt_type = data[0]

        if pkt_type == PKT_INFO:
            filename, file_size = parse_info(data)
            transfers[addr] = {'filename': filename, 'file_size': file_size, 'chunks': {}}
            print(f"[SERVER] Receiving '{filename}' ({file_size} bytes) from {addr}")

        elif pkt_type == PKT_DATA:
            if addr not in transfers:
                print(f"[WARNING] PKT_DATA from unknown sender {addr}, ignoring.")
                continue
            chunk_number, chunk_data = parse_data(data)
            transfers[addr]['chunks'][chunk_number] = chunk_data

            ack_pkt = build_ack(chunk_number) # sends the acknowledgment for the received chunk back to the sender
            sock.sendto(ack_pkt, addr)

            print(f"[SERVER] Received chunk {chunk_number} from {addr}")

        elif pkt_type == PKT_CHECKSUM:
            if addr not in transfers:
                print(f"[WARNING] PKT_CHECKSUM from unknown sender {addr}, ignoring.")
                continue

            received_hash = parse_checksum(data)
            transfer = transfers[addr]
            file_bytes = b''.join(transfer['chunks'][i] for i in sorted(transfer['chunks']))
            print(f"[SERVER] Received checksum from {addr}. Verifying file integrity...")
            if compute_checksum(file_bytes) == received_hash:
                filepath = os.path.join(STORAGE, transfer['filename'])
                with open(filepath, 'wb') as f:
                    f.write(file_bytes)
                print(f"[SERVER] '{transfer['filename']}' saved successfully!")
            else:
                print(f"[SERVER] Checksum mismatch! '{transfer['filename']}' discarded.")

            # print(transfers)
            del transfers[addr]  # removes the transfer record for this sender after processing

if __name__ == "__main__":
    main()