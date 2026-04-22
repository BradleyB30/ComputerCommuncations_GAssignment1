import os
import socket
import sys

from shared_protocol import recv_file_bytes, recv_line, send_file_bytes, send_line


BUFFER_SIZE = 4096
STORAGE_DIR = "server_storage"


def is_safe_filename(name: str) -> bool:
    # Restrict file access to simple filenames so transfers stay inside server_storage.
    if not name:
        return False
    if "/" in name or "\\" in name or ".." in name:
        return False
    return os.path.basename(name) == name


def handle_ls(conn) -> None:
    # Send the current list of files available on the server.
    entries = []
    for name in sorted(os.listdir(STORAGE_DIR)):
        path = os.path.join(STORAGE_DIR, name)
        if os.path.isfile(path):
            entries.append(name)
    payload = "\n".join(entries).encode("utf-8")
    send_line(conn, f"OK {len(payload)}")
    if payload:
        conn.sendall(payload)


def handle_get(conn, filename: str) -> None:
    # Send a requested server file to the client if it exists.
    if not is_safe_filename(filename):
        send_line(conn, "ERR Invalid filename")
        return

    path = os.path.join(STORAGE_DIR, filename)
    if not os.path.isfile(path):
        send_line(conn, "ERR File not found")
        return

    size = os.path.getsize(path)
    send_line(conn, f"OK {size}")
    send_file_bytes(conn, path)


def handle_put(conn, filename: str, size: int) -> None:
    # Receive an uploaded file from the client and save it on the server.
    if not is_safe_filename(filename):
        send_line(conn, "ERR Invalid filename")
        return
    if size < 0:
        send_line(conn, "ERR Invalid file size")
        return

    path = os.path.join(STORAGE_DIR, filename)
    send_line(conn, "OK Ready")
    try:
        recv_file_bytes(conn, path, size)
    except ConnectionError:
        if os.path.exists(path):
            os.remove(path)
        raise
    except OSError:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
        send_line(conn, "ERR Failed to store file")
        return
    send_line(conn, "OK Upload complete")


def handle_client(conn, addr) -> None:
    # Process commands for one connected client until it quits or disconnects.
    print(f"Connected: {addr[0]}:{addr[1]}")
    while True:
        try:
            command_line = recv_line(conn).strip()
        except ConnectionError:
            print(f"Disconnected: {addr[0]}:{addr[1]}")
            break

        if not command_line:
            send_line(conn, "ERR Invalid command")
            continue

        parts = command_line.split()
        command = parts[0].upper()

        if command == "LS" and len(parts) == 1:
            handle_ls(conn)
        elif command == "GET" and len(parts) == 2:
            handle_get(conn, parts[1])
        elif command == "PUT" and len(parts) == 3:
            try:
                size = int(parts[2])
            except ValueError:
                send_line(conn, "ERR Invalid file size")
                continue
            try:
                handle_put(conn, parts[1], size)
            except ConnectionError:
                print(f"Upload interrupted: {addr[0]}:{addr[1]}")
                break
            except OSError as exc:
                send_line(conn, f"ERR Server file error: {exc}")
        elif command == "QUIT" and len(parts) == 1:
            send_line(conn, "OK Goodbye")
            print(f"Session closed: {addr[0]}:{addr[1]}")
            break
        else:
            send_line(conn, "ERR Invalid command")


def start_server(port: int) -> None:
    # Create the FTP server socket, listen on the chosen port, and serve clients sequentially.
    os.makedirs(STORAGE_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen()
        print(f"Server listening on port {port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                handle_client(conn, addr)


def main() -> None:
    # Parse the server port from the command line and start the FTP server.
    if len(sys.argv) != 2:
        print("Usage: python serv.py <PORTNUMBER>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    if not 1 <= port <= 65535:
        print("Port must be between 1 and 65535.")
        sys.exit(1)

    try:
        start_server(port)
    except OSError as exc:
        print(f"Server error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
