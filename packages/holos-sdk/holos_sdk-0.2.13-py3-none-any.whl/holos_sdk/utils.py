"""
Utility functions for the Holos SDK.

This module contains shared utility functions used across different parts of the SDK.
"""

import json
import uuid
import logging
from typing import List, Union, Optional, Any
from a2a.server.events import EventQueue
from a2a.types import Message, Part, TextPart, Role
from .types import Plan

logger = logging.getLogger(__name__)


def plan_to_message(plan: Plan) -> Message:
    """
    Convert a Plan object to a Message object.
    
    Args:
        plan: The Plan object to convert
        
    Returns:
        A Message object representing the plan
    """
    
    # Create a text part with the plan information in todo list style
    plan_text = f"📋 **Plan:** {plan.goal}\n"
    if plan.depend_plans:
        plan_text += "\n📝 **Dependencies:**\n"
        plan_text += format_dependencies(plan.depend_plans, level=1)

    text_part = TextPart(text=plan_text)
    part = Part(root=text_part)
    
    # Convert plan to JSON string for metadata
    plan_json = plan.model_dump_json()
    
    # Create message with plan metadata
    message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.agent,
        parts=[part],
        metadata={"plan_object": plan_json}  # Add plan as JSON string for easy recovery
    )
    
    return message


def format_dependencies(depend_plans: List[Union[str, 'Plan']], level: int = 1) -> str:
    """
    Format dependencies as a hierarchical todo list.
    
    Args:
        depend_plans: List of dependency plans (can be strings or Plan objects)
        level: Current indentation level for nested dependencies
        
    Returns:
        Formatted string with hierarchical todo list
    """
    result = ""
    indent = "  " * level
    
    for dep_plan in depend_plans:
        if isinstance(dep_plan, str):
            result += f"{indent}- [ ] {dep_plan}\n"
        else:
            result += f"{indent}- [ ] {dep_plan.goal}\n"
            # Recursively format sub-dependencies
            if dep_plan.depend_plans:
                result += format_dependencies(dep_plan.depend_plans, level + 1)
    
    return result


def try_convert_to_plan(message: Message) -> Optional[Plan]:
    """
    Try to convert a message to a Plan object.
    
    This method looks for plan data in the message metadata, following the same
    pattern used by the client-side _plan_to_message() method.
    
    Args:
        message: The message to convert
        
    Returns:
        Plan object if conversion is successful, None otherwise
    """
    try:
        # Check metadata for plan information (same pattern as client-side)
        if hasattr(message, 'metadata') and message.metadata and 'plan_object' in message.metadata:
            plan_data = json.loads(message.metadata['plan_object'])
            return Plan(**plan_data)
        
        return None
    except Exception as e:
        logger.error(f"Error converting message to plan: {e}")
        return None
