import os


BUFFER_SIZE = 4096


def send_line(sock, line: str) -> None:
    # Send one newline-terminated control message over the socket.
    if not line.endswith("\n"):
        line = f"{line}\n"
    sock.sendall(line.encode("utf-8"))


def recv_line(sock) -> str:
    # Read one newline-terminated control message from the socket.
    chunks = bytearray()
    while True:
        data = sock.recv(1)
        if not data:
            if chunks:
                break
            raise ConnectionError("Connection closed while waiting for a line.")
        if data == b"\n":
            break
        chunks.extend(data)
    return chunks.decode("utf-8").rstrip("\r")


def recv_exact(sock, size: int) -> bytes:
    # Read an exact number of bytes so file transfers do not truncate or over-read.
    chunks = bytearray()
    while len(chunks) < size:
        data = sock.recv(min(BUFFER_SIZE, size - len(chunks)))
        if not data:
            raise ConnectionError("Connection closed before receiving expected bytes.")
        chunks.extend(data)
    return bytes(chunks)


def send_file_bytes(sock, path: str) -> None:
    # Stream a local file to the peer in fixed-size binary chunks.
    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendall(chunk)


def recv_file_bytes(sock, path: str, size: int) -> None:
    # Receive a fixed-size file payload from the peer and save it locally.
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as file_handle:
        remaining = size
        while remaining > 0:
            chunk = recv_exact(sock, min(BUFFER_SIZE, remaining))
            file_handle.write(chunk)
            remaining -= len(chunk)
