"""
This module provides a tool to execute display commands on multiple devices 
in a GNS3 topology using Nornir.
"""
import json
import os
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_multiline
from langchain.tools import BaseTool
from gns3_copilot.public_model import get_device_ports_from_topology
from gns3_copilot.log_config import setup_tool_logger

# config log
logger = setup_tool_logger("display_tools_nornir")

# Load environment variables
load_dotenv()

# Nornir configuration groups
groups_data = {
    "cisco_IOSv_telnet": {
        "platform": "cisco_ios",
        "hostname": os.getenv("GNS3_SERVER_HOST"),
        "timeout": 120,
        "username": os.getenv("GNS3_SERVER_USERNAME"),
        "password": os.getenv("GNS3_SERVER_PASSWORD"),
        "connection_options": {
            "netmiko": {
                "extras": {
                    "device_type": "cisco_ios_telnet"
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

class ExecuteMultipleDeviceCommands(BaseTool):
    """
    A tool to execute display (show) commands on multiple devices in a GNS3 topology using Nornir.
    This class uses Nornir to manage connections and execute commands on multiple devices 
    concurrently.

    **Important:**
    This tool is strictly for read-only operations.
    It is forbidden to execute any configuration commands, including 'configure terminal' or 
    any command that changes device state.
    Only use this tool for safe, non-intrusive 'show' or display commands.
    """

    name: str = "execute_multiple_device_commands"
    description: str = """
    Executes display (show) commands on multiple devices in the current GNS3 topology.
    Input should be a JSON array containing device names and their respective commands to execute.
    Example input:
        [
            {
                "device_name": "R-1",
                "commands": ["show version", "show ip interface brief"]
            },
            {
                "device_name": "R-2", 
                "commands": ["show version", "show ip ospf neighbor"]
            }
        ]
    Returns a list of dictionaries, each containing the device name and command outputs.

    **Do NOT use this tool for any configuration commands (such as 'configure terminal').**
    """

    def _run(
        self,
        tool_input: str,
        run_manager=None
        ) -> List[Dict[str, Any]]:  # pylint: disable=unused-argument
        """
        Executes display commands on multiple devices in the current GNS3 topology.

        Args:
            tool_input (str): A JSON string containing a list of device commands to
            execute.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing device names and
            command outputs.
        """

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

        # Execute all devices concurrently in a single run
        try:
            task_result = dynamic_nr.run(
                task=self._run_all_device_configs_with_single_retry,
                device_configs_map=device_configs_map
            )

            # Process results for all devices
            results = self._process_task_results(device_configs_list, hosts_data, task_result)

        except Exception as e:
            # Overall execution failed
            logger.error("Error executing display on all devices: %s", e)
            return [{"error": f"Execution error: {str(e)}"}]

        logger.info(
            "Multiple device display execution completed. Results: %s",
            json.dumps(results, indent=2, ensure_ascii=False)
        )

        return results

    def _run_all_device_configs_with_single_retry(
        self,
        task: Task,
        device_configs_map: Dict[str, List[str]]
        ) -> Result:
        """Execute display commands with single retry mechanism."""
        device_name = task.host.name
        config_commands = device_configs_map.get(device_name, [])

        if not config_commands:
            return Result(host=task.host, result="No display commands to execute")

        try:
            _result = task.run(
                task=netmiko_multiline,
                commands=config_commands,
                enable=True,
                read_timeout=60,
            )
            return Result(host=task.host, result=_result.result)

        except Exception as e:
        # Handle prompt detection issues with Cisco IOSv L2 images where the '#' prompt character
        # may be delayed, causing Netmiko prompt detection failures. Implements retry logic.
            if "netmiko_multiline (failed)" in str(e):
                _result = task.run(
                    task=netmiko_multiline,
                    commands=config_commands,
                    enable=True,
                    read_timeout=60,
                )
                return Result(host=task.host, result=_result.result)

            logger.error("display failed for device %s: %s", device_name, e)
            return Result(
                host=task.host,
                result=f"display failed (Unhandled Exception): {str(e)}",
                failed=True
            )

    def _validate_tool_input(self, tool_input: Union[str, bytes, List, Dict]):
        """
        Validate device display command input, handling both JSON string 
        and already parsed Python object inputs from different LLM providers.
        
        Args:
            tool_input: The input received from the LangChain/LangGraph tool call.
        """

        device_configs_list = None

        # Compatibility Check and Parsing ---
        # Check if the input is a string (or bytes) which needs to be parsed.
        if isinstance(tool_input, (str, bytes, bytearray)):
            # Handle models (like potentially DeepSeek) that return a raw JSON string.
            try:
                device_configs_list = json.loads(tool_input)
                logger.info("Successfully parsed tool input from JSON string.")
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON string received as tool input: %s", e)
                return [{"error": f"Invalid JSON string input from model: {e}"}]
        else:
            # Handle standard models (like GPT/OpenAI) where the framework
            # has already parsed the JSON into a Python object (dict or list).
            device_configs_list = tool_input
            logger.info("Using tool input directly as type: %s", {type(tool_input).__name__})

        # Core Business Logic Validation ---
        # Check if the final object is the expected Python list type.
        if not isinstance(device_configs_list, list):
            # If the result of parsing/direct use is not a list, raise an error.
            error_msg = (
                "Tool input must result in a JSON array/Python list,"
                f" but got {type(device_configs_list).__name__}"
                )
            logger.error(error_msg)
            return [{"error": error_msg}]

        # Further validation (e.g., ensuring the list is not empty)
        if not device_configs_list:
            logger.warning("Tool input list is empty.")
            # Decide whether to return an error based on business requirements
            return []

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

    def _process_task_results(self, device_configs_list, hosts_data, task_result):
        """Process the task results and format them for return."""
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
                    f"Configuration execution failed: {multi_result[0].result}"
                    )
                device_result["output"] = multi_result[0].result
            else:
                # Execution successful
                device_result["status"] = "success"
                device_result["output"] = multi_result[0].result
                device_result["config_commands"] = config_commands

            results.append(device_result)

        return results


if __name__ == "__main__":
    # Example usage
    device_commands = json.dumps(
        [
            {
                "device_name": "R-2",
                "commands": ["show version", "show ip interface brief"]
            },
            {
                "device_name": "R-1",
                "commands": ["show version", "show ip interface brief"]
            },
            {
                "device_name": "SW-1",
                "commands": ["show version", "show ip interface brief"]
            },
            {
                "device_name": "SW-2",
                "commands": ["show version", "show ip interface brief"]
            }
        ]
    )

    exe_cmd = ExecuteMultipleDeviceCommands()

    failed_count = 0

    for i in range(0, 1):
        exe_results = exe_cmd._run(tool_input=device_commands)
        for result in exe_results:
            for result in exe_results:
                if result.get("status") == "failed":
                    failed_count += 1

    print(f"Failed Count: {failed_count}")

    #print("Execution results:")
    #print(json.dumps(result, indent=2, ensure_ascii=False))
