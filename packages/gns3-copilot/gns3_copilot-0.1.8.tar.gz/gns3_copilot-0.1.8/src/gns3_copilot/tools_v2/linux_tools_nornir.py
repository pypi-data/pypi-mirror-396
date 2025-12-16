"""
This module uses Nornir + Netmiko to batch execute Linux commands on GNS3 topology devices
via Telnet console.
"""
import json
import os
import re
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from langchain.tools import BaseTool
from gns3_copilot.public_model import get_device_ports_from_topology
from gns3_copilot.log_config import setup_tool_logger

# config log
logger = setup_tool_logger("linux_tools_nornir")

# Load environment variables
load_dotenv()

# Linux Telnet dedicated connection group
# (using generic_telnet driver, suitable for GNS3 console)
# Nornir configuration groups
groups_data = {
    "linux_telnet": {
        "platform": "linux",
        "hostname": os.getenv("GNS3_SERVER_HOST"),
        "timeout": 120,
        "username": os.getenv("LINUX_TELNET_USERNAME"),
        "password": os.getenv("LINUX_TELNET_PASSWORD"),
        "connection_options": {
            "netmiko": {
                "platform": "linux",
                "extras": {
                    "device_type": "generic_telnet",
                    #"use_timing": True,
                    "global_delay_factor": 3,
                    "timeout": 120,
                    "fast_cli": False,
                }
            }
        }
    }
}

defaults = {
    "data": {
        "location": "gns3"
    }
}

class LinuxTelnetBatchTool(BaseTool):
    """
    A tool to batch execute read-only commands on multiple Linux devices (Telnet console)
    in GNS3 labs.

    **Important:**
    This tool is strictly for operations. Configuration commands are prohibited.
    """

    name: str = "linux_telnet_batch_commands"
    description: str = """
    Batch execute commands on multiple Linux devices in current GNS3 topology via Telnet console.
    Input should be a JSON array containing device names and their respective commands to execute.
    Example input:
        [
            {
                "device_name": "debian01",
                "commands": ["uname -a", "df -h", "sudo docker ps"]
            },
            {
                "device_name": "ubuntu01", 
                "commands": ["ip a", "uptime"]
            }
        ]
    Returns a list of dictionaries, each containing the device name and command outputs.

    If you need to start the server/client for testing, execute the command one device at a time, do not execute them simultaneously.
    
    **Do NOT use this tool for any Danger configuration commands.**
    
    ALL commands generated must be strictly non-interactive and non-paginated.
    Prohibited commands include top, vi/nano, and using pipes to less or more.
    For continuous tasks, use single-run alternatives (e.g., ping -c 1, ps -aux instead of top).
    Output must exit immediately after execution.
    """

    def _run(
        self,
        tool_input: str,
        run_manager=None
        ) -> List[Dict[str, Any]]:  # pylint: disable=unused-argument
        """
        Batch execute Linux read-only commands (main entry).

        Args:
            tool_input (str): A JSON string containing a list of device commands to
            execute.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing device names and
            command outputs.
        """
        if not os.getenv("LINUX_TELNET_USERNAME") or not os.getenv("LINUX_TELNET_PASSWORD"):
            user_message = (
                    "Sorry, I can't proceed just yet.\n\n"
                    "You haven't configured the Linux login credentials (username and password) yet.\n"
                    "Please go to the **Settings** page and fill in the Linux username and password under the login credentials section.\n\n"
                    "Once you've saved them, just come back and say anything (like 'Done' or 'Configured'), "
                    "and I'll immediately continue with the task!\n\n"
                    "Need help finding the settings page? Let me know — happy to guide you!"
                )
            logger.warning("Linux login credentials not configured — user prompted to set them up")
            return [
                    {
                        "error": user_message,
                        "action_required": "configure_linux_credentials",
                        "user_message": user_message  # optional, if your frontend uses a separate field
                    }
                ]
        # Validate input
        device_configs_list = self._validate_tool_input(tool_input)
        if (isinstance(device_configs_list, list)
            and len(device_configs_list) > 0
            and "error"
            in device_configs_list[0]
            ):
            return device_configs_list

        # Create a mapping of device names to their display commands
        device_configs_map = self._configs_map(device_configs_list)

        # Prepare device hosts data
        try:
            hosts_data = self._prepare_device_hosts_data(device_configs_list)
        except ValueError as e:
            logger.error("Failed to prepare device hosts data: %s", e)
            return [{"error": str(e)}]

        # Initialize Nornir
        try:
            dynamic_nr = self._initialize_nornir(hosts_data)
        except ValueError as e:
            logger.error("Failed to initialize Nornir: %s", e)
            return [{"error": str(e)}]

        results = []

        # Execute login first, then commands
        try:
            # Step 1: Execute login for all devices
            login_result = dynamic_nr.run(task=self._linux_telnet_login)

            # Step 2: Check login results and execute commands for successful logins
            successful_logins = []
            failed_logins = []

            for device_name, result in login_result.items():
                if result.failed:
                    failed_logins.append(device_name)
                    logger.error("Device %s login failed: %s", device_name, result.result)
                else:
                    successful_logins.append(device_name)
                    logger.info("Device %s login successful: %s", device_name, result.result)

            # Step 3: Execute commands only for devices with successful login
            if successful_logins:
                # Filter device_configs_map to only include successfully logged in devices
                filtered_device_configs_map = {
                    device_name: commands
                    for device_name, commands in device_configs_map.items()
                    if device_name in successful_logins
                }

                task_result = dynamic_nr.run(
                    task=self._run_all_device_configs_with_single_retry,
                    device_configs_map=filtered_device_configs_map
                )
            else:
                task_result = {}

            # Step 4: Process results for all devices
            results = self._process_task_results(
                device_configs_list, hosts_data, task_result, login_result)

        except Exception as e:
            # Overall execution failed
            logger.error("Error executing display on all devices: %s", e)
            return [{"error": f"Execution error: {str(e)}"}]

        logger.info(
            "Multiple device display execution completed. Results: %s",
            json.dumps(results, indent=2, ensure_ascii=False)
        )

        return results

    def _linux_telnet_login(self, task: Task) -> Result:
        """Smart Linux Telnet login: detect login status and only login when needed."""
        try:
            net_connect = task.host.get_connection("netmiko", task.nornir.config)

            # Clear the buffer + press Enter several times to wake up the device.
            net_connect.clear_buffer()
            time.sleep(0.3)
            net_connect.write_channel("\n\n")

            # Read the device output (wait up to 10 seconds)
            output = net_connect.read_channel_timing(read_timeout=10)
            logger.info("Device %s initial output: %s", task.host.name, output)

            # Check if output contains "login:" prompt
            if re.search(r"(?i)(^|\n).{0,60}(debian\s+)?login:\s*$", output):
                # Need to login, execute login process
                logger.info("Device %s requires login - detected login prompt", task.host.name)

                # Send username
                net_connect.write_channel(f"{task.host.username}\n")
                time.sleep(1)
                output = net_connect.read_until_prompt_or_pattern("Password:", read_timeout=10)

                # Send password
                net_connect.write_channel(f"{task.host.password}\n")
                time.sleep(1)
                output += net_connect.read_until_prompt_or_pattern(r"[$#]", read_timeout=10)

                logger.info("Device %s login successful", task.host.name)
                return Result(host=task.host, result="Login successful")

            # Already logged in, return directly
            logger.info(
                "Device %s already logged in - no login prompt detected",
                task.host.name)
            return Result(host=task.host, result="Already logged in")

        except Exception as e:
            logger.error("Device %s login failed: %s", task.host.name, e)
            return Result(host=task.host, result=f"Login failed: {str(e)}", failed=True)

    def _run_all_device_configs_with_single_retry(
        self,
        task: Task,
        device_configs_map: Dict[str, List[str]]
        ) -> Result:
        """
        Execute commands one-by-one on a single device
        (optimized for generic_telnet + $ prompt).
        """
        device_name = task.host.name
        config_commands = device_configs_map.get(device_name, [])

        if not config_commands:
            return Result(host=task.host, result="No display commands to execute")

        _outputs = {}
        for _cmd in config_commands:
            try:
                # Use timing mode + increased delay_factor to ensure stability with $ prompt
                # and passwordless sudo
                _result = task.run(
                    task=netmiko_send_command,
                    command_string=_cmd,
                    use_timing=True,
                    delay_factor=3,
                    max_loops=5000,
                )
                _outputs[_cmd] = _result.result
            except Exception as e:
                _outputs[_cmd] = f"Command execution failed: {str(e)}"

        return Result(host=task.host, result=_outputs)

    def _validate_tool_input(self, tool_input):
        """Validate and parse the JSON input for device display commands."""
        try:
            device_configs_list = json.loads(tool_input)
            if not isinstance(device_configs_list, list):
                return [{"error": "Input must be a JSON array of device display objects"}]
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return [{"error": f"Invalid JSON input: {e}"}]

        return device_configs_list

    def _configs_map(self, device_config_list):
        """Create a mapping of device names to their display commands."""
        device_configs_map = {}
        for device_config in device_config_list:
            device_name = device_config["device_name"]
            config_commands = device_config["commands"]
            device_configs_map[device_name] = config_commands

        return device_configs_map

    def _prepare_device_hosts_data(self, device_config_list):
        """Prepare device hosts data from topology information."""
        # Extract device names list
        device_names = [device_config["device_name"] for device_config in device_config_list]

        # Get device port information
        hosts_data = get_device_ports_from_topology(device_names)

        if not hosts_data:
            raise ValueError(
                "Failed to get device information from topology or no valid devices found"
                )
        # Force all devices to use linux_telnet group (compatible with generic_telnet)
        for _, _host_info in hosts_data.items():
            _host_info["groups"] = ["linux_telnet"]

        # Check for missing devices
        missing_devices = set(device_names) - set(hosts_data.keys())
        if missing_devices:
            logger.warning("Some devices not found in topology: %s", missing_devices)

        return hosts_data

    def _initialize_nornir(self, hosts_data):
        """Initialize Nornir with the provided hosts data."""
        try:
            return InitNornir(
                inventory={
                    "plugin": "DictInventory",
                    "options": {
                        "hosts": hosts_data,
                        "groups": groups_data,
                        "defaults": defaults,
                    },
                },
                runner={
                    "plugin": "threaded",
                    "options": {
                        "num_workers": 10
                    },
                },
                logging={
                    "enabled": False
                },
            )
        except Exception as e:
            logger.error("Failed to initialize Nornir: %s", e)
            raise ValueError(f"Failed to initialize Nornir: {e}") from e

    def _process_task_results(
        self, device_configs_list, hosts_data, task_result, login_result=None):
        """Process task results and format them for return."""
        results = []

        for device_config in device_configs_list:
            device_name = device_config["device_name"]
            config_commands = device_config["commands"]

            # Check if device is in topology
            if device_name not in hosts_data:
                device_result = {
                    "device_name": device_name,
                    "status": "failed",
                    "error": (
                        f"Device '{device_name}' not found in topology or missing console_port"
                        )
                }
                results.append(device_result)
                continue

            # Check login result first
            if login_result and device_name in login_result:
                login_status = login_result[device_name]
                if login_status.failed:
                    device_result = {
                        "device_name": device_name,
                        "status": "failed",
                        "error": f"Login failed: {login_status.result}",
                        "login_status": login_status.result
                    }
                    results.append(device_result)
                    continue

            # Check if device has execution results
            if device_name not in task_result:
                device_result = {
                    "device_name": device_name,
                    "status": "failed", 
                    "error": (
                        f"Device '{device_name}' not found in task results"
                        )
                }
                results.append(device_result)
                continue

            # Process execution results
            multi_result = task_result[device_name]
            device_result = {"device_name": device_name}

            if multi_result[0].failed:
                # Execution failed
                device_result["status"] = "failed"
                device_result["error"] = (
                    f"Command execution failed: {multi_result[0].result}"
                    )
                device_result["output"] = multi_result[0].result
            else:
                # Execution successful
                device_result["status"] = "success"
                device_result["output"] = multi_result[0].result
                device_result["config_commands"] = config_commands

            # Add login status if available
            if login_result and device_name in login_result:
                device_result["login_status"] = login_result[device_name].result

            results.append(device_result)

        return results


if __name__ == "__main__":
    # Example usage
    device_commands = json.dumps(
        [
            {
                "device_name": "Debian12.6-1",
                "commands": [
                    "uname -a",
                    "hostnamectl || hostname",
                    "cat /etc/os-release",
                    "whoami && id",
                    "id",
                    "pwd",
                    "top -b -n 1 | head -20",
                    "ip neigh show | grep -v REACHABLE | grep -v PERMANENT",
                    "ping -c 3 114.114.114.114",
                    "ps aux --sort=-%mem | head -15",
                    "journalctl -u ssh --no-pager -n 20",
                    "find /etc -name \"*.conf\" | head -10",
                    ]
            },
            {
                "device_name": "Debian12.6-2",
                "commands": [
                    "uname -a",
                    "hostnamectl || hostname",
                    "cat /etc/os-release",
                    "whoami && id",
                    "id",
                    "pwd",
                    "top -b -n 1 | head -20",
                    "ip neigh show | grep -v REACHABLE | grep -v PERMANENT",
                    "ping -c 3 114.114.114.114",
                    "ps aux --sort=-%mem | head -15",
                    "journalctl -u ssh --no-pager -n 20",
                    "find /etc -name \"*.conf\" | head -10",
                    ]
            },
        ]
    )

    exe_cmd = LinuxTelnetBatchTool()

    failed_count = 0

    for i in range(0, 1):
        exe_results = exe_cmd._run(tool_input=device_commands)
        for exe_result in exe_results:
            for exe_result in exe_results:
                if exe_result.get("status") == "failed":
                    failed_count += 1

    print("Execution results:")
    print(json.dumps(exe_results, indent=2, ensure_ascii=False))
    print(f"Failed Count: {failed_count}")
