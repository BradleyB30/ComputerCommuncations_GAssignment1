import os
import socket
import sys

from shared_protocol import recv_exact, recv_file_bytes, recv_line, send_file_bytes, send_line


STORAGE_DIR = "client_storage"


def is_safe_filename(name: str) -> bool:
    # Restrict file transfers to simple filenames so client storage stays contained.
    if not name:
        return False
    if "/" in name or "\\" in name or ".." in name:
        return False
    return os.path.basename(name) == name


def cmd_ls(sock) -> None:
    # Request and display the list of files currently stored on the server.
    send_line(sock, "LS")
    response = recv_line(sock)
    if response.startswith("ERR "):
        print(f"Server error: {response[4:]}")
        return

    parts = response.split(maxsplit=1)
    if len(parts) != 2 or parts[0] != "OK":
        print("Server error: Invalid response")
        return

    try:
        payload_size = int(parts[1])
    except ValueError:
        print("Server error: Invalid response")
        return

    payload = recv_exact(sock, payload_size).decode("utf-8") if payload_size else ""
    if not payload:
        print("No files on server.")
        return

    print("Files on server:")
    for name in payload.split("\n"):
        print(name)


def cmd_get(sock, filename: str) -> None:
    # Download one file from the server into the local client storage folder.
    if not is_safe_filename(filename):
        print("Invalid filename.")
        return

    send_line(sock, f"GET {filename}")
    response = recv_line(sock)
    if response.startswith("ERR "):
        print(f"Server error: {response[4:]}")
        return

    parts = response.split(maxsplit=1)
    if len(parts) != 2 or parts[0] != "OK":
        print("Server error: Invalid response")
        return

    try:
        file_size = int(parts[1])
    except ValueError:
        print("Server error: Invalid response")
        return

    destination = os.path.join(STORAGE_DIR, filename)
    recv_file_bytes(sock, destination, file_size)
    print("Download complete")


def cmd_put(sock, filename: str) -> None:
    # Upload one local file from the client storage folder to the server.
    if not is_safe_filename(filename):
        print("Invalid filename.")
        return

    path = os.path.join(STORAGE_DIR, filename)
    if not os.path.isfile(path):
        print("Local file not found")
        return

    file_size = os.path.getsize(path)
    send_line(sock, f"PUT {filename} {file_size}")

    response = recv_line(sock)
    if response.startswith("ERR "):
        print(f"Server error: {response[4:]}")
        return
    if response != "OK Ready":
        print("Server error: Invalid response")
        return

    send_file_bytes(sock, path)

    response = recv_line(sock)
    if response.startswith("ERR "):
        print(f"Server error: {response[4:]}")
        return
    if response != "OK Upload complete":
        print("Server error: Invalid response")
        return

    print("Upload complete")


def cmd_quit(sock) -> None:
    # Tell the server the session is ending, then close the client connection.
    try:
        send_line(sock, "QUIT")
        response = recv_line(sock)
        if response == "OK Goodbye":
            print("Disconnected from server")
        elif response.startswith("ERR "):
            print(f"Server error: {response[4:]}")
    except OSError:
        pass
    finally:
        sock.close()


def repl_loop(sock) -> None:
    # Run the interactive FTP prompt and translate user commands into socket requests.
    while True:
        try:
            raw_command = input("ftp> ").strip()
        except EOFError:
            print()
            cmd_quit(sock)
            break

        if not raw_command:
            continue

        parts = raw_command.split(maxsplit=1)
        command = parts[0].lower()

        try:
            if command == "ls" and len(parts) == 1:
                cmd_ls(sock)
            elif command == "get" and len(parts) == 2:
                cmd_get(sock, parts[1])
            elif command == "put" and len(parts) == 2:
                cmd_put(sock, parts[1])
            elif command == "quit" and len(parts) == 1:
                cmd_quit(sock)
                break
            else:
                print("Invalid command. Use ls, get <filename>, put <filename>, or quit.")
        except ConnectionError as exc:
            print(f"Connection lost: {exc}")
            break
        except OSError as exc:
            print(f"Connection error: {exc}")
            break


def connect_to_server(host: str, port: int):
    # Open a TCP connection to the FTP server using the provided host and port.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def main() -> None:
    # Parse client arguments, connect to the server, and start the interactive prompt.
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server machine> <server port>")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    if not 1 <= port <= 65535:
        print("Port must be between 1 and 65535.")
        sys.exit(1)

    os.makedirs(STORAGE_DIR, exist_ok=True)

    try:
        sock = connect_to_server(host, port)
    except OSError as exc:
        print(f"Connection error: {exc}")
        sys.exit(1)

    with sock:
        repl_loop(sock)


if __name__ == "__main__":
    main()
