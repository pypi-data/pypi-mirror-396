import socket


def find_available_port(start_port=8080, host="127.0.0.1"):
    """
    Find the first available TCP port starting from `start_port`.
    """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port  # success
            except OSError:
                port += 1  # try next one
