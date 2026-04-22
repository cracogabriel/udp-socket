import struct
import hashlib

"""
info package
| 1 byte: pkt_type | 1 byte: filename_size | N bytes: filename | 4 bytes: file_size |
"""
PKT_INFO     = 1  # first packet: filename + file size

"""
datas package
| 1 byte: pkt_type | 4 bytes: chunk_number | 2 bytes: data_size | N bytes: data |
"""
PKT_DATA     = 2  # data chunk: chunk number + up to 1024 bytes

"""
checksum package
| 1 byte: pkt_type | 20 bytes: SHA-1 hash |
"""
PKT_CHECKSUM = 3  # last packet: SHA-1 hash of the full file

"""
ack package
| 1 byte: pkt_type | 4 bytes: chunk_number |
"""
PKT_ACK = 4  # acknowledgment: chunk number being acknowledged

# PKT_ACK ______________________________________

def build_ack(chunk_number: int) -> bytes:
    return struct.pack('!BI', PKT_ACK, chunk_number) # pkt_type + chunk_number

def parse_ack(data: bytes) -> int:
    chunk_number = struct.unpack('!I', data[1:5])[0]
    return chunk_number


# PKT_INFO ____________________________________

def build_info(filename: str, file_size: int) -> bytes:
    filename_bytes = filename.encode('utf-8')
    packet  = struct.pack('!BB', PKT_INFO, len(filename_bytes))  # pkt_type + filename_size
    packet += filename_bytes                                     # filename
    packet += struct.pack('!I', file_size)                       # file_size (4 bytes)
    return packet

def parse_info(data: bytes) -> tuple:
    filename_size = data[1]
    filename = data[2 : 2 + filename_size].decode('utf-8')
    file_size = struct.unpack('!I', data[2 + filename_size : 6 + filename_size])[0]
    return filename, file_size

# PKT_DATA ______________________________________

def build_data(chunk_number: int, data: bytes) -> bytes:
    packet  = struct.pack('!BIH', PKT_DATA, chunk_number, len(data))
    packet += data
    return packet

def parse_data(data: bytes) -> tuple:
    chunk_number, data_size = struct.unpack('!IH', data[1:7])
    chunk_data = data[7 : 7 + data_size]
    return chunk_number, chunk_data

# PKT_CHECKSUM ___________________________________

def build_checksum(file_bytes: bytes) -> bytes:
    sha1 = hashlib.sha1(file_bytes).digest()  # sempre 20 bytes
    packet = struct.pack('B', PKT_CHECKSUM) + sha1
    return packet

def parse_checksum(data: bytes) -> bytes:
    return data[1:21]  # os 20 bytes do SHA-1


# Checksum _______________________________________

def compute_checksum(file_bytes: bytes) -> bytes:
    return hashlib.sha1(file_bytes).digest()