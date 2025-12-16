from loguru import logger
import paramiko
import socket
import time
from paramiko import SSHClient
import select
import threading


def test_ssh_connection(hostname, username, password=None, key_filename=None, port=22):
    """
    Tests an SSH connection to a remote host.

    Args:
        hostname (str): The hostname or IP address of the remote SSH server.
        username (str): The username for authentication.
        password (str, optional): The password for authentication. Defaults to None.
        key_filename (str, optional): Path to the private key file for authentication. Defaults to None.
        port (int, optional): The SSH port. Defaults to 22.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Auto-add new host keys

    try:
        if password:
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                banner_timeout=60,
                timeout=60,
                auth_timeout=60,
            )
        elif key_filename:
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                key_filename=key_filename,
                banner_timeout=60,
                timeout=60,
                auth_timeout=60,
            )
        else:
            logger.error(
                "Error: Either password or key_filename must be provided for authentication."
            )
            return False

        logger.info(f"Successfully connected to {hostname} as {username}")
        return True
    except paramiko.AuthenticationException:
        logger.debug(f"Authentication failed for {username} on {hostname}")
        return False
    except paramiko.SSHException as exception:
        logger.debug(f"SSH error connecting to {hostname}: {exception}")
        return False
    except socket.error as exception:
        logger.debug(f"Socket error connecting to {hostname}: {exception}")
        return False
    except Exception as exception:
        logger.debug(f"An unexpected error occurred: {exception}")
        return False
    finally:
        ssh_client.close()


TEN_MINUTES = 60 * 10


def wait_for_ssh(
    hostname, username, password=None, key_filename=None, port=22, timeout=TEN_MINUTES
):
    """
    Waits until an SSH connection to a remote host can be established.

    Args:
        hostname (str): The hostname or IP address of the remote SSH server.
        username (str): The username for authentication.
        password (str, optional): The password for authentication. Defaults to None.
        key_filename (str, optional): Path to the private key file for authentication. Defaults to None.
        port (int, optional): The SSH port. Defaults to 22.
        timeout (int, optional): Maximum time to wait in seconds. Defaults to 300.

    Returns:
        bool: True if the connection is successful within the timeout, False otherwise.
    """

    start_time = time.time()
    while time.time() - start_time < timeout:
        if test_ssh_connection(
            hostname, username, password=password, key_filename=key_filename, port=port
        ):
            return True
        logger.debug(f"Waiting for SSH to become available on {hostname}...")
        time.sleep(10)

    logger.warning(
        f"Timeout reached: Unable to connect to {hostname} via SSH within {timeout} seconds."
    )
    return False


def run_command(
    hostname,
    username,
    command: str,
    password=None,
    key_filename=None,
    port=22,
):
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        key_filename=key_filename,
    )
    stdin, stdout, stderr = ssh_client.exec_command(command)

    stdout_string = stdout.read().decode("utf-8").rstrip("\n")
    stderr_string = stderr.read().decode("utf-8").rstrip("\n")
    if stdout_string != b"":
        logger.info(stdout_string)
    if stderr_string != b"":
        logger.error(stderr_string)

    ssh_client.close()


def _pump(s1, s2):
    try:
        while True:
            r, _, _ = select.select([s1, s2], [], [])
            if s1 in r:
                try:
                    data = s1.recv(32768)
                except (ConnectionResetError, OSError) as e:
                    logger.debug(f"local->remote recv error: {e}")
                    break
                if not data:
                    break
                try:
                    s2.sendall(data)
                except (BrokenPipeError, OSError) as e:
                    logger.debug(f"remote send error: {e}")
                    break

            if s2 in r:
                try:
                    data = s2.recv(32768)
                except (ConnectionResetError, OSError) as e:
                    logger.debug(f"remote->local recv error: {e}")
                    break
                if not data:
                    break
                try:
                    s1.sendall(data)
                except (BrokenPipeError, OSError) as e:
                    logger.debug(f"local send error: {e}")
                    break
    finally:
        for s in (s1, s2):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass


def start_port_forward(
    hostname,
    username,
    port=22,
    keyfile=None,
    password=None,
    local_hostname="127.0.0.1",
    local_port=8080,
    remote_hostname="george-michael",
    remote_port=443,
):
    """
    Start a local port forward (ssh -L equivalent).
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    logger.info(f"Connecting to {hostname}:{port} as {username}...")
    client.connect(
        hostname,
        port=port,
        username=username,
        key_filename=keyfile,
        password=password,
        allow_agent=True,
        look_for_keys=True,
        timeout=15,
    )

    transport = client.get_transport()
    if not transport:
        logger.error("Failed to get SSH transport.")
        client.close()
        return

    transport.set_keepalive(30)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((local_hostname, local_port))
    listener.listen(50)
    logger.info(
        f"Listening on {local_hostname}:{local_port} -> {remote_hostname}:{remote_port}"
    )

    try:
        while True:
            client_sock, client_addr = listener.accept()
            chan = transport.open_channel(
                kind="direct-tcpip",
                dest_addr=(remote_hostname, remote_port),
                src_addr=client_addr,
            )
            t = threading.Thread(target=_pump, args=(client_sock, chan), daemon=True)
            t.start()
    except KeyboardInterrupt:
        logger.info("Port forward stopped.")
    finally:
        listener.close()
        client.close()
