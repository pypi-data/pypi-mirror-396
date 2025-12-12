import uuid
from typing import Dict


def create_config(config_data: Dict) -> dict:
    """
    Create a configuration dictionary for the graphs.
    """
    thread_id = str(uuid.uuid4())

    # Combine all configuration data
    return {
        "configurable": {
            **config_data,  # Unpack the original config data
            "thread_id": thread_id,  # Add the generated thread ID
        },
    }
