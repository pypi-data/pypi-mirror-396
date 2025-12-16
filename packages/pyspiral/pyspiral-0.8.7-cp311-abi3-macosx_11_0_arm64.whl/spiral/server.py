import socket
import time

import httpx


def wait_for_port(port: int, host: str = "localhost", timeout: float = 5.0):
    """Wait until a port starts accepting TCP connections."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.time() - start_time >= timeout:
                raise TimeoutError(
                    f"Waited too long for the port {port} on host {host} to start accepting connections."
                ) from ex


def wait_for_healthy(port: int, host: str = "localhost", timeout: float = 5.0):
    """Wait until a server port is accepting connections and responding to health checks."""
    # First wait for server to start accepting TCP connections
    wait_for_port(port, host, timeout)

    # Then wait for the server to be healthy
    start_time = time.time()
    while True:
        try:
            response = httpx.get(f"http://{host}:{port}/health", timeout=timeout)
            if response.status_code == 200:
                break
        except (httpx.HTTPError, httpx.ConnectError) as ex:
            time.sleep(0.01)
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Waited too long for the port {port} on host {host} to become healthy.") from ex
