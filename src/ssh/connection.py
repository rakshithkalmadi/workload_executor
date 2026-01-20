import paramiko
import os
from contextlib import contextmanager
from typing import Tuple, Optional
from loguru import logger

class SSHConnection:
    def __init__(self, host: str, username: str, key_path: str):
        self.host = host
        self.username = username
        self.key_path = key_path
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self):
        """Establishes the SSH connection."""
        if self._client:
            return

        try:
            logger.info(f"Connecting to {self.username}@{self.host} using key {self.key_path}")
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            key = paramiko.RSAKey.from_private_key_file(self.key_path)
            self._client.connect(
                hostname=self.host,
                username=self.username,
                pkey=key,
                timeout=10
            )
            logger.info("SSH connection established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}: {e}")
            self._client = None
            raise

    def disconnect(self):
        """Closes the SSH connection."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("SSH connection closed.")

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Executes a command on the remote server.
        Returns: (stdout, stderr, exit_code)
        """
        if not self._client:
            self.connect()

        logger.debug(f"Executing command: {command}")
        try:
            stdin, stdout, stderr = self._client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            
            out_str = stdout.read().decode('utf-8').strip()
            err_str = stderr.read().decode('utf-8').strip()
            
            return out_str, err_str, exit_status
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return "", str(e), -1

    @contextmanager
    def connection(self):
        """Context manager for ephemeral connections."""
        try:
            self.connect()
            yield self
        finally:
            self.disconnect()
