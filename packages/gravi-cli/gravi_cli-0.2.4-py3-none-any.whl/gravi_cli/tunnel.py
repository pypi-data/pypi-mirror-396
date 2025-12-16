"""
Database tunnel client for gravi CLI.

Establishes WebSocket tunnels to database services in burner namespaces,
exposing them on local ports for tools like MongoDB Compass or redis-cli.
"""

import asyncio
import json
import socket
import signal
import sys
from typing import NamedTuple

import websockets
from websockets.exceptions import ConnectionClosed


class ServiceConfig(NamedTuple):
    """Configuration for a tunneled service."""
    name: str
    default_port: int
    connection_string_template: str


# Service definitions
SERVICES = {
    "mongo": ServiceConfig(
        name="MongoDB",
        default_port=27017,
        connection_string_template="mongodb://localhost:{port}/?directConnection=true",
    ),
    "redis": ServiceConfig(
        name="Redis",
        default_port=6379,
        connection_string_template="redis://localhost:{port}",
    ),
}


def find_available_port(preferred: int, max_attempts: int = 10) -> int:
    """
    Find an available port, starting with the preferred port.

    Args:
        preferred: The preferred port to try first
        max_attempts: Maximum number of ports to try

    Returns:
        An available port number

    Raises:
        RuntimeError: If no available port is found
    """
    for offset in range(max_attempts):
        port = preferred + offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found near {preferred}")


class TunnelClient:
    """Manages WebSocket tunnels to burner database services."""

    def __init__(self, mom_url: str, token: str, burner_id: str):
        """
        Initialize tunnel client.

        Args:
            mom_url: Base URL for mom API (e.g., "https://mom.gravitate.energy/api")
            token: Access token for authentication
            burner_id: Burner instance ID
        """
        self.mom_url = mom_url.rstrip("/")
        self.token = token
        self.burner_id = burner_id
        self._servers: list[asyncio.Server] = []
        self._shutdown_event = asyncio.Event()

    def _get_ws_url(self, service: str) -> str:
        """Get WebSocket URL for a service tunnel (no token in URL)."""
        # Convert HTTP to WebSocket URL
        ws_url = self.mom_url.replace("https://", "wss://").replace("http://", "ws://")
        return f"{ws_url}/burners/{self.burner_id}/tunnel/{service}"

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        service: str,
    ) -> None:
        """Handle a single client connection by relaying to WebSocket."""
        ws_url = self._get_ws_url(service)

        try:
            async with websockets.connect(ws_url) as ws:
                # Send auth message first (token not in URL for security)
                auth_message = json.dumps({"type": "auth", "token": self.token})
                await ws.send(auth_message)

                async def tcp_to_ws():
                    try:
                        while True:
                            data = await reader.read(65536)
                            if not data:
                                break
                            await ws.send(data)
                    except Exception:
                        pass

                async def ws_to_tcp():
                    try:
                        async for message in ws:
                            if isinstance(message, bytes):
                                writer.write(message)
                                await writer.drain()
                    except ConnectionClosed:
                        pass
                    except Exception:
                        pass

                # Run both directions concurrently
                tcp_task = asyncio.create_task(tcp_to_ws())
                ws_task = asyncio.create_task(ws_to_tcp())

                done, pending = await asyncio.wait(
                    [tcp_task, ws_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

        except websockets.exceptions.InvalidStatusCode as e:
            # Extract close reason if available
            print(f"  Connection failed: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Connection error: {e}", file=sys.stderr)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _start_service_tunnel(self, service: str) -> tuple[int, bool]:
        """
        Start a local TCP server for a service.

        Returns:
            Tuple of (port, port_was_fallback)
        """
        config = SERVICES[service]
        preferred_port = config.default_port

        # Find available port
        port = find_available_port(preferred_port)
        was_fallback = port != preferred_port

        async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            await self._handle_client(reader, writer, service)

        server = await asyncio.start_server(
            client_handler,
            "127.0.0.1",
            port,
        )
        self._servers.append(server)

        return port, was_fallback

    async def run(self) -> None:
        """
        Start all service tunnels and wait for shutdown.

        Prints connection strings and waits for Ctrl+C.
        """
        print(f"\nConnecting to {self.burner_id}...\n")

        # Start tunnels for all services
        results = {}
        for service in SERVICES:
            try:
                port, was_fallback = await self._start_service_tunnel(service)
                results[service] = (port, was_fallback)
            except RuntimeError as e:
                print(f"Warning: Could not start {service} tunnel: {e}", file=sys.stderr)

        if not results:
            print("Error: No tunnels could be started", file=sys.stderr)
            return

        # Print connection info
        print("=" * 60)
        print("Tunnels active - Press Ctrl+C to disconnect")
        print("=" * 60)
        print()

        for service, (port, was_fallback) in results.items():
            config = SERVICES[service]
            conn_str = config.connection_string_template.format(port=port)
            fallback_note = f"  ({config.default_port} in use)" if was_fallback else ""
            print(f"{config.name}:".ljust(10) + f"{conn_str}{fallback_note}")

        print()
        print("=" * 60)

        # Wait for shutdown signal
        await self._shutdown_event.wait()

    def shutdown(self) -> None:
        """Signal shutdown to close all tunnels."""
        self._shutdown_event.set()
        for server in self._servers:
            server.close()


async def run_tunnel(mom_url: str, token: str, burner_id: str) -> None:
    """
    Main entry point for running database tunnels.

    Args:
        mom_url: Base URL for mom API
        token: Access token for authentication
        burner_id: Burner instance ID
    """
    client = TunnelClient(mom_url, token, burner_id)

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler():
        print("\n\nDisconnecting...")
        client.shutdown()

    # Handle both SIGINT (Ctrl+C) and SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    try:
        await client.run()
    except KeyboardInterrupt:
        signal_handler()
