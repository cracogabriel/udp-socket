import struct

MSG_NORMAL    = 1
MSG_EMOJI     = 2
MSG_URL       = 3
MSG_ECHO_REQ  = 4  
MSG_ECHO_RES  = 5 

"""
Package docs:

- tipo de mensagem [1 byte]
- tamanho apelido (tam_apl) [1 byte]
- apelido [tam_apl (1 a 64) bytes ]
- tamanho mensagem (tam_msg) [1 byte]
- mensagem [tam_msg bytes]

"""


def build_packet(msg_type: int, nickname: str, message: str) -> bytes:
    nickname_bytes = nickname.encode('utf-8')[:64]  #limits to 64 bytes, if the nickname is longer, it will be truncated
    msg_bytes = message.encode('utf-8')[:255]  #limits to 255 bytes, if the message is longer, it will be truncated

    packet  = struct.pack('BB', msg_type, len(nickname_bytes))   # msg_type + len_nickname 
    packet += nickname_bytes                                     # nickname
    packet += struct.pack('B', len(msg_bytes))                   # len_message
    packet += msg_bytes                                          # message

    return packet


def parse_packet(data: bytes) -> tuple:
    # We need at least 3 bytes: msg_type + len_nickname + len_message
    if len(data) < 3:
        return None

    msg_type   = data[0]
    len_nickname = data[1]

    # [using package docs: line 10] Make sure the nickname bytes are actually there, skips the first 2 bytes (msg_type + len_nickname), skips the len of nickname and checks if the message length byte is there (1 byte after the nickname)
    if len(data) < 2 + len_nickname + 1:
        return None

    nickname = data[2 : 2 + len_nickname].decode('utf-8')

    len_message = data[2 + len_nickname]
    message     = data[3 + len_nickname : 3 + len_nickname + len_message].decode('utf-8')

    return msg_type, nickname, message