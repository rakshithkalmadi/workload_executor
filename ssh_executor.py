"""
SSH Executor Module
Executes installation commands from ResponseFormat on a remote VM via SSH.
"""
import os
import yaml
import paramiko
from dataclasses import dataclass
from typing import Optional


def load_config(config_path: str = "./config/system_configuration.yaml") -> dict:
    """Load VM configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def execute_on_remote(
    installation_steps: list[str],
    download_urls: list[str],
    verification_command: Optional[str] = None,
    config_path: str = "./config/system_configuration.yaml",
    working_dir: str = "/tmp/workload"
) -> bool:
    """
    Execute installation steps on remote VM via SSH.
    
    Args:
        installation_steps: List of shell commands to execute
        download_urls: List of download URLs (for reference/logging)
        verification_command: Command to verify installation (optional)
        config_path: Path to VM configuration YAML
        working_dir: Remote directory to work in
    
    Returns:
        True if all commands succeeded, False otherwise
    """
    # Load configuration
    config = load_config(config_path)
    hostname = config["remote_ip"]
    username = config["username"]
    key_file = config["key_file"]
    
    print(f"[SSH] Connecting to {username}@{hostname}...")
    
    # Setup SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect using private key
        key = paramiko.RSAKey.from_private_key_file(key_file)
        client.connect(hostname=hostname, username=username, pkey=key, timeout=30)
        print(f"[SSH] Connected successfully!")
        
        # Create working directory
        setup_cmd = f"mkdir -p {working_dir} && cd {working_dir}"
        print(f"[SSH] Setting up working directory: {working_dir}")
        stdin, stdout, stderr = client.exec_command(setup_cmd)
        stdout.channel.recv_exit_status()
        
        # Execute each installation step
        all_success = True
        for i, cmd in enumerate(installation_steps, 1):
            # Prepend cd to working dir for each command
            full_cmd = f"cd {working_dir} && {cmd}"
            print(f"\n[{i}/{len(installation_steps)}] Executing: {cmd}")
            print("-" * 60)
            
            stdin, stdout, stderr = client.exec_command(full_cmd, timeout=300)
            
            # Stream stdout
            for line in stdout:
                print(f"  {line.strip()}")
            
            # Check for errors
            err_output = stderr.read().decode().strip()
            if err_output:
                print(f"  [STDERR] {err_output}")
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"  [FAILED] Exit code: {exit_status}")
                all_success = False
                # Continue with other commands instead of stopping
            else:
                print(f"  [OK]")
        
        # Run verification command if provided
        if verification_command:
            print(f"\n[VERIFY] Running: {verification_command}")
            print("-" * 60)
            full_cmd = f"cd {working_dir} && {verification_command}"
            stdin, stdout, stderr = client.exec_command(full_cmd, timeout=60)
            
            for line in stdout:
                print(f"  {line.strip()}")
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print(f"  [VERIFICATION PASSED]")
            else:
                print(f"  [VERIFICATION FAILED] Exit code: {exit_status}")
                all_success = False
        
        return all_success
        
    except paramiko.AuthenticationException:
        print(f"[ERROR] Authentication failed for {username}@{hostname}")
        return False
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH connection failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    finally:
        client.close()
        print("\n[SSH] Connection closed.")


def execute_response(response) -> bool:
    """
    Execute a ResponseFormat object on remote VM.
    
    Args:
        response: ResponseFormat dataclass with installation_steps, download_urls, verification_command
    
    Returns:
        True if execution succeeded, False otherwise
    """
    print("=" * 60)
    print(f"SOFTWARE: {response.summary[:80]}...")
    print(f"DOWNLOAD URLs: {len(response.download_urls)} found")
    for url in response.download_urls:
        print(f"  - {url}")
    print("=" * 60)
    
    return execute_on_remote(
        installation_steps=response.installation_steps,
        download_urls=response.download_urls,
        verification_command=response.verification_command
    )


if __name__ == "__main__":
    # Test with a sample response
    @dataclass
    class TestResponse:
        summary: str
        installation_steps: list[str]
        download_urls: list[str]
        verification_command: str | None
    
    test_resp = TestResponse(
        summary="Test software",
        installation_steps=[
            "echo 'Hello from remote!'",
            "uname -a",
            "pwd"
        ],
        download_urls=[],
        verification_command="echo 'Verification complete'"
    )
    
    success = execute_response(test_resp)
    print(f"\nExecution {'succeeded' if success else 'failed'}")
