import sys
from network import create_socket, send_packet, start_receiver
from protocol import build_packet, MSG_NORMAL, MSG_EMOJI, MSG_URL, MSG_ECHO_REQ

def print_help():
    print("Commands: /emoji <msg> | /url <link> | /echo <msg> | /quit | /help")

def main():
    if len(sys.argv) != 5:
        print("Usage: python chat_udp.py <my_ip> <my_port> <dest_ip> <dest_port>")
        sys.exit(1)

    my_ip     = sys.argv[1]
    my_port   = int(sys.argv[2])
    dest_ip   = sys.argv[3]
    dest_port = int(sys.argv[4])

    nickname = input("Enter your nickname: ").strip()[:64]

    sock = create_socket(my_ip, my_port)
    start_receiver(sock, nickname)

    print(f"Chat started on {my_ip}:{my_port}")
    print(f"Sending to {dest_ip}:{dest_port}")
    print_help()
    print("-" * 50)

    while True:
        user_input = input(">> ").strip()

        if user_input == "/quit":
            print("Closing chat...")
            break
        elif user_input.startswith("/emoji "):
            packet = build_packet(MSG_EMOJI, nickname, user_input[7:])
        elif user_input.startswith("/url "):
            packet = build_packet(MSG_URL, nickname, user_input[5:])
        elif user_input.startswith("/echo "):
            packet = build_packet(MSG_ECHO_REQ, nickname, user_input[6:])
        elif user_input == "/help":
            print_help()
            continue
        else:
            packet = build_packet(MSG_NORMAL, nickname, user_input)

        send_packet(sock, packet, dest_ip, dest_port)

    sock.close()



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nServer shutting down.')