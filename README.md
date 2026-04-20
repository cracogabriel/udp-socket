# Q1: UDP P2P Chat

A peer-to-peer chat application built with Python's native `socket` library. Each peer sends and receives messages simultaneously using threads, following a custom binary protocol over UDP.

## Problem Statement

Proposed by Prof. Rodrigo Campiolo as part of the Distributed Systems course. The goal is to implement a P2P chat where clients exchange messages directly with each other using UDP sockets and a structured binary protocol supporting different message types (normal, emoji, URL, and ECHO).

---

## Project Structure

```
q1/
├── chat_udp.py      # Entry point: starts the peer, reads terminal input and sends packets
├── network.py       # Socket creation, packet sending, and receiver thread
└── protocol.py      # build_packet / parse_packet and message type constants
```

---

## Requirements

- Python 3.8+
- No external libraries required

---

## How to Run

Open **two terminals** at the project root.

**Terminal 1: Peer A:**

```bash
python chat_udp.py 127.0.0.1 5000 127.0.0.1 5001
```

**Terminal 2: Peer B:**

```bash
python chat_udp.py 127.0.0.1 5001 127.0.0.1 5000
```

> Each peer binds to its own port and sends to the other's port.  
> To connect from another machine, replace `127.0.0.1` with the target machine's IP address.

---

## Supported Commands

| Command         | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `<text>`        | Sends a normal message                                              |
| `/emoji <text>` | Sends a message of type emoji                                       |
| `/url <link>`   | Sends a message of type URL                                         |
| `/echo <text>`  | Sends an ECHO request to check if the other peer is active          |
| `/help`         | Displays available commands (local only, not sent over the network) |
| `/quit`         | Closes the chat                                                     |

---

## Binary Protocol

All communication uses a **binary protocol** with variable-length fields.

### Packet structure

```
| 1 byte: Message Type | 1 byte: Nickname Size | N bytes: Nickname | 1 byte: Message Size | N bytes: Message |
```

### Field constraints

| Field         | Size    | Constraint      |
| ------------- | ------- | --------------- |
| Message Type  | 1 byte  | See table below |
| Nickname Size | 1 byte  | 1 to 64         |
| Nickname      | N bytes | UTF-8 encoded   |
| Message Size  | 1 byte  | 0 to 255        |
| Message       | N bytes | UTF-8 encoded   |

### Message type identifiers

| Type         | Code |
| ------------ | ---- |
| MSG_NORMAL   | 0x01 |
| MSG_EMOJI    | 0x02 |
| MSG_URL      | 0x03 |
| MSG_ECHO_REQ | 0x04 |
| MSG_ECHO_RES | 0x05 |

### ECHO flow

To avoid infinite loops, ECHO is split into two distinct types:

```
Peer A  --MSG_ECHO_REQ-->  Peer B   (Peer A asks if Peer B is active)
Peer A  <--MSG_ECHO_RES--  Peer B   (Peer B confirms and does not reply again)
```

---

## Architecture

Each peer runs **two concurrent execution flows**:

- **Main thread**: blocked on `input()`, reads user commands and sends packets
- **Receiver thread**: blocked on `recvfrom()`, listens for incoming packets and prints them

The receiver thread is started as a `daemon`, meaning it is automatically terminated when the main thread exits.

---

## Error Handling

- **Peer:** `Ctrl+C` exits cleanly without a traceback.
- **Peer:** Malformed packets (too short or incomplete) are detected in `parse_packet` and discarded with a warning.
- **Peer:** Nicknames longer than 64 characters and messages longer than 255 characters are silently truncated before sending.
