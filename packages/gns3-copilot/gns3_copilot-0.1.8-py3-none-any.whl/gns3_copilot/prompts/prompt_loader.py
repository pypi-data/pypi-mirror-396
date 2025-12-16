"""
Dynamic prompt loader for GNS3 Network Automation Assistant

This module provides functionality to dynamically load system prompts based on English proficiency levels.
It supports loading different prompts for A1, A2, B1, B2, C1, and C2 English levels from environment variables.
"""

import os
import importlib
from gns3_copilot.log_config import setup_logger

logger = setup_logger("prompt_loader")

# Mapping of English levels to their corresponding prompt modules
ENGLISH_LEVEL_PROMPT_MAP = {
    "NORMAL PROMPT": "react_prompt",
    "A1": "english_level_prompt_a1",
    "A2": "english_level_prompt_a2", 
    "B1": "english_level_prompt_b1",
    "B2": "english_level_prompt_b2",
    "C1": "english_level_prompt_c1",
    "C2": "english_level_prompt_c2"
}

def _load_react_prompt():
    """
    Load the react_prompt system prompt.
    
    Returns:
        str: The react_prompt system prompt content.
        
    Raises:
        ImportError: If there's an error importing the react_prompt module.
        AttributeError: If the SYSTEM_PROMPT is not found in the react_prompt module.
    """
    try:
        # Import the react_prompt module
        react_prompt_module = importlib.import_module("gns3_copilot.prompts.react_prompt")
        
        # Get the SYSTEM_PROMPT from the module
        if hasattr(react_prompt_module, 'SYSTEM_PROMPT'):
            system_prompt = getattr(react_prompt_module, 'SYSTEM_PROMPT')
            logger.info("Successfully loaded react_prompt")
            return system_prompt
        else:
            raise AttributeError("SYSTEM_PROMPT not found in react_prompt module")
            
    except ImportError as e:
        logger.error("Failed to import react_prompt module: %s", e)
        raise ImportError(f"Failed to import react_prompt module: {e}")
    
    except AttributeError as e:
        logger.error("Error accessing SYSTEM_PROMPT in react_prompt module: %s", e)
        raise AttributeError(f"Error accessing SYSTEM_PROMPT in react_prompt module: {e}")

def load_system_prompt(level=None):
    """
    Load system prompt based on English proficiency level.
    
    Args:
        level (str, optional): English proficiency level (A1, A2, B1, B2, C1, C2).
                              If not provided, will read from ENGLISH_LEVEL environment variable.
                              If environment variable is not set or invalid, will use react_prompt.
    
    Returns:
        str: The system prompt content for the specified English level or react_prompt.
        
    Raises:
        ImportError: If there's an error importing the prompt module.
        AttributeError: If the SYSTEM_PROMPT is not found in the module.
    """
    # Determine the English level to use
    if not level:
        level = os.getenv("ENGLISH_LEVEL", "")
    
    # Normalize level to uppercase
    level = level.upper().strip()
    
    
    # If no valid English level is specified, use react_prompt
    if not level or level not in ENGLISH_LEVEL_PROMPT_MAP:
        logger.info("No valid English level specified (got '%s'), using react_prompt", level)
        return _load_react_prompt()
    
    # Get the module name for the level
    module_name = ENGLISH_LEVEL_PROMPT_MAP[level]
    
    try:
        # Import the module dynamically
        prompt_module = importlib.import_module(f"gns3_copilot.prompts.{module_name}")
        
        # Get the SYSTEM_PROMPT from the module
        if hasattr(prompt_module, 'SYSTEM_PROMPT'):
            system_prompt = getattr(prompt_module, 'SYSTEM_PROMPT')
            logger.info("Successfully loaded system prompt for English level: %s", level)
            return system_prompt
        else:
            raise AttributeError(f"SYSTEM_PROMPT not found in module {module_name}")
            
    except ImportError as e:
        logger.error("Failed to import prompt module '%s': %s", module_name, e)
        # Fallback to react_prompt
        logger.info("Falling back to react_prompt due to import error")
        return _load_react_prompt()
    
    except AttributeError as e:
        logger.error("Error accessing SYSTEM_PROMPT in module '%s': %s", module_name, e)
        # Fallback to react_prompt
        logger.info("Falling back to react_prompt due to attribute error")
        return _load_react_prompt()
