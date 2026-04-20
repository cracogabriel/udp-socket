import socket
import threading
from protocol import parse_packet, MSG_ECHO_REQ, MSG_ECHO_RES, MSG_NORMAL, MSG_EMOJI, MSG_URL
from protocol import build_packet

def create_socket(ip: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    return sock

def send_packet(sock: socket.socket, packet: bytes, dest_ip: str, dest_port: int) -> None:
    sock.sendto(packet, (dest_ip, dest_port))


def receive_loop(sock: socket.socket, my_nickname: str) -> None:
    while True:
        data, addr = sock.recvfrom(4096)   # blocking

        result = parse_packet(data)
        if result is None:
            print("[WARNING] Malformed packet received, ignoring.")
            continue

        msg_type, nickname, message = result

        if msg_type == MSG_ECHO_REQ:
            response = build_packet(MSG_ECHO_RES, my_nickname, message)
            sock.sendto(response, addr)
            print(f"\n[ECHO] {nickname} asked if you're active. Replied his message \"{message}\"!")

        elif msg_type == MSG_ECHO_RES:
            print(f"\n[ECHO] {nickname} is active ({addr[0]}:{addr[1]}): {message}")

        elif msg_type == MSG_NORMAL:
            print(f"\n[{nickname}]: {message}")

        elif msg_type == MSG_EMOJI:
            print(f"\n[{nickname}] 😊 {message}")

        elif msg_type == MSG_URL:
            print(f"\n[{nickname}] 🔗 {message}")

        print(">> ", end='', flush=True)  


def start_receiver(sock: socket.socket, my_nickname: str) -> None:
    thread = threading.Thread(target=receive_loop, args=(sock, my_nickname), daemon=True)
    thread.start()