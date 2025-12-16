"""
GNS3 template retrieval tool for device discovery.

Provides functionality to retrieve all available device templates
from a GNS3 server, including template names, IDs, and types.
"""

import json
import os
from pprint import pprint
from dotenv import load_dotenv
from langchain.tools import BaseTool
from gns3_copilot.gns3_client import Gns3Connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_get_node_temp")

# Load environment variables
load_dotenv()

class GNS3TemplateTool(BaseTool):
    """
    A LangChain tool to retrieve all available device templates from a GNS3 server.
    The tool connects to the GNS3 server and extracts the name, template_id, and template_type
    for each template.

    **Input:**
    No input is required for this tool. It connects to the GNS3 server at the default URL
    (http://localhost:3080) and retrieves all templates.

    **Output:**
    A dictionary containing a list of dictionaries, each with the name, template_id, and
    template_type of a template. Example output:
        {
            "templates": [
                {"name": "Router1", "template_id": "uuid1", "template_type": "qemu"},
                {"name": "Switch1", "template_id": "uuid2", "template_type": "ethernet_switch"}
            ]
        }
    If an error occurs, returns a dictionary with an error message.
    """

    name: str = "get_gns3_templates"
    description: str = """
    Retrieves all available device templates from a GNS3 server.
    Returns a dictionary containing a list of dictionaries, each with the name, template_id,
    and template_type of a template. No input is required.
    Example output:
        {
            "templates": [
                {"name": "Router1", "template_id": "uuid1", "template_type": "qemu"},
                {"name": "Switch1", "template_id": "uuid2", "template_type": "ethernet_switch"}
            ]
        }
    If the connection fails, returns a dictionary with an error message.
    """

    def _run(self, tool_input: str = "", run_manager=None) -> dict:
        """
        Connects to the GNS3 server and retrieves a list of all available device templates.

        Args:
            tool_input (str): Optional input (not used in this tool).
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary containing the list of templates or an error message.
        """
        try:
            # Initialize Gns3Connector
            logger.info("Connecting to GNS3 server at %s...", os.getenv("GNS3_SERVER_URL"))
            
            if os.getenv("API_VERSION") == '2':
                gns3_server = Gns3Connector(
                    url=os.getenv("GNS3_SERVER_URL"),
                    api_version=os.getenv("API_VERSION")
                    )
            if os.getenv("API_VERSION") == '3':
                gns3_server = Gns3Connector(
                    url=os.getenv("GNS3_SERVER_URL"),
                    user=os.getenv("GNS3_SERVER_USERNAME"),
                    cred=os.getenv("GNS3_SERVER_PASSWORD"),
                    api_version=os.getenv("API_VERSION")
                    )
                

            # Retrieve all available templates
            templates = gns3_server.get_templates()

            # Extract name, template_id, and template_type
            template_info = [
                {
                    "name": template.get("name", "N/A"),
                    "template_id": template.get("template_id", "N/A"),
                    "template_type": template.get("template_type", "N/A")
                }
                for template in templates
            ]

            # Log the retrieved templates
            logger.debug(
                "Retrieved templates: %s", json.dumps(template_info, indent=2, ensure_ascii=False)
                )

            # Return JSON-formatted result
            return {"templates": template_info}

        except Exception as e:
            logger.error("Failed to connect to GNS3 server or retrieve templates: %s", e)
            return {"error": f"Failed to retrieve templates: {str(e)}"}

if __name__ == "__main__":
    # Test the tool locally
    tool = GNS3TemplateTool()
    result = tool._run("")
    pprint(result)
