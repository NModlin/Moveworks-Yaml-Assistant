"""
Moveworks Built-in Actions Catalog.

This module contains the catalog of Moveworks built-in actions (mw.*) with their
input argument specifications and typical JSON output examples.

Based on Section 7 and Table 2 of the Source of Truth Document.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class InputArgSpec:
    """
    Specification for an input argument of a Moveworks action.
    
    Attributes:
        name: Name of the input argument
        type: Expected data type (str, int, bool, list, dict)
        required: Whether this argument is required
        description: Description of the argument
        default_value: Default value if not required
    """
    name: str
    type: str
    required: bool = True
    description: str = ""
    default_value: Any = None


@dataclass
class MWAction:
    """
    Represents a Moveworks built-in action.
    
    Attributes:
        action_name: Full action name (e.g., "mw.get_user_by_email")
        display_name: Human-readable name for UI
        description: Description of what the action does
        input_args: List of input argument specifications
        typical_json_output_example: Example JSON output structure
        category: Category for grouping actions
    """
    action_name: str
    display_name: str
    description: str
    input_args: List[InputArgSpec] = field(default_factory=list)
    typical_json_output_example: Optional[str] = None
    category: str = "General"


# Moveworks Built-in Actions Catalog
MW_ACTIONS_CATALOG = [
    # User Management Actions
    MWAction(
        action_name="mw.get_user_by_email",
        display_name="Get User by Email",
        description="Retrieve user information by email address",
        input_args=[
            InputArgSpec("email", "str", True, "Email address of the user to retrieve")
        ],
        typical_json_output_example="""{
  "user": {
    "id": "user123",
    "email": "john.doe@company.com",
    "name": "John Doe",
    "department": "Engineering",
    "manager": {
      "id": "mgr456",
      "email": "jane.smith@company.com",
      "name": "Jane Smith"
    },
    "active": true
  }
}""",
        category="User Management"
    ),
    
    MWAction(
        action_name="mw.get_user_by_id",
        display_name="Get User by ID",
        description="Retrieve user information by user ID",
        input_args=[
            InputArgSpec("user_id", "str", True, "Unique identifier of the user")
        ],
        typical_json_output_example="""{
  "user": {
    "id": "user123",
    "email": "john.doe@company.com",
    "name": "John Doe",
    "department": "Engineering",
    "manager": {
      "id": "mgr456",
      "email": "jane.smith@company.com",
      "name": "Jane Smith"
    },
    "active": true
  }
}""",
        category="User Management"
    ),
    
    MWAction(
        action_name="mw.get_all_users",
        display_name="Get All Users",
        description="Retrieve a list of all users in the organization",
        input_args=[
            InputArgSpec("limit", "int", False, "Maximum number of users to return", 100),
            InputArgSpec("department", "str", False, "Filter by department", None)
        ],
        typical_json_output_example="""{
  "users": [
    {
      "id": "user123",
      "email": "john.doe@company.com",
      "name": "John Doe",
      "department": "Engineering",
      "active": true
    },
    {
      "id": "user456",
      "email": "jane.smith@company.com",
      "name": "Jane Smith",
      "department": "Engineering",
      "active": true
    }
  ],
  "total_count": 2,
  "has_more": false
}""",
        category="User Management"
    ),
    
    # Communication Actions
    MWAction(
        action_name="mw.send_email",
        display_name="Send Email",
        description="Send an email message",
        input_args=[
            InputArgSpec("to", "str", True, "Recipient email address"),
            InputArgSpec("subject", "str", True, "Email subject"),
            InputArgSpec("body", "str", True, "Email body content"),
            InputArgSpec("cc", "str", False, "CC email addresses (comma-separated)", None),
            InputArgSpec("bcc", "str", False, "BCC email addresses (comma-separated)", None)
        ],
        typical_json_output_example="""{
  "message_id": "msg_abc123",
  "status": "sent",
  "sent_at": "2025-01-27T10:30:00Z",
  "recipients": {
    "to": ["john.doe@company.com"],
    "cc": [],
    "bcc": []
  }
}""",
        category="Communication"
    ),
    
    MWAction(
        action_name="mw.send_slack_message",
        display_name="Send Slack Message",
        description="Send a message to a Slack channel or user",
        input_args=[
            InputArgSpec("channel", "str", True, "Slack channel or user ID"),
            InputArgSpec("message", "str", True, "Message content"),
            InputArgSpec("thread_ts", "str", False, "Thread timestamp for replies", None)
        ],
        typical_json_output_example="""{
  "message_id": "slack_msg_xyz789",
  "channel": "#general",
  "timestamp": "1706356200.123456",
  "status": "sent",
  "permalink": "https://company.slack.com/archives/C1234567890/p1706356200123456"
}""",
        category="Communication"
    ),
    
    # IT Service Management Actions
    MWAction(
        action_name="mw.create_ticket",
        display_name="Create IT Ticket",
        description="Create a new IT service ticket",
        input_args=[
            InputArgSpec("title", "str", True, "Ticket title/summary"),
            InputArgSpec("description", "str", True, "Detailed description"),
            InputArgSpec("priority", "str", False, "Ticket priority (low, medium, high, critical)", "medium"),
            InputArgSpec("category", "str", False, "Ticket category", "General"),
            InputArgSpec("assignee", "str", False, "Assignee email or ID", None)
        ],
        typical_json_output_example="""{
  "ticket": {
    "id": "TICK-12345",
    "title": "Password Reset Request",
    "description": "User needs password reset for email account",
    "status": "open",
    "priority": "medium",
    "category": "Account Access",
    "created_at": "2025-01-27T10:30:00Z",
    "assignee": {
      "id": "agent123",
      "name": "IT Support Agent",
      "email": "support@company.com"
    },
    "requester": {
      "id": "user456",
      "name": "John Doe",
      "email": "john.doe@company.com"
    }
  }
}""",
        category="IT Service Management"
    ),
    
    MWAction(
        action_name="mw.update_ticket",
        display_name="Update IT Ticket",
        description="Update an existing IT service ticket",
        input_args=[
            InputArgSpec("ticket_id", "str", True, "Ticket ID to update"),
            InputArgSpec("status", "str", False, "New ticket status", None),
            InputArgSpec("priority", "str", False, "New priority", None),
            InputArgSpec("comment", "str", False, "Comment to add", None),
            InputArgSpec("assignee", "str", False, "New assignee", None)
        ],
        typical_json_output_example="""{
  "ticket": {
    "id": "TICK-12345",
    "title": "Password Reset Request",
    "status": "in_progress",
    "priority": "medium",
    "updated_at": "2025-01-27T11:00:00Z",
    "last_comment": "Working on password reset",
    "assignee": {
      "id": "agent123",
      "name": "IT Support Agent",
      "email": "support@company.com"
    }
  }
}""",
        category="IT Service Management"
    ),
    
    # HTTP Actions
    MWAction(
        action_name="mw.http_request",
        display_name="HTTP Request",
        description="Make an HTTP request to an external API",
        input_args=[
            InputArgSpec("url", "str", True, "Target URL"),
            InputArgSpec("method", "str", False, "HTTP method (GET, POST, PUT, DELETE)", "GET"),
            InputArgSpec("headers", "dict", False, "HTTP headers", {}),
            InputArgSpec("body", "str", False, "Request body (for POST/PUT)", None),
            InputArgSpec("timeout", "int", False, "Request timeout in seconds", 30)
        ],
        typical_json_output_example="""{
  "status_code": 200,
  "headers": {
    "content-type": "application/json",
    "content-length": "156"
  },
  "body": {
    "data": "response data",
    "success": true
  },
  "response_time_ms": 245
}""",
        category="Integration"
    )
]


def get_action_by_name(action_name: str) -> Optional[MWAction]:
    """Get a Moveworks action by its name."""
    for action in MW_ACTIONS_CATALOG:
        if action.action_name == action_name:
            return action
    return None


def get_actions_by_category(category: str) -> List[MWAction]:
    """Get all actions in a specific category."""
    return [action for action in MW_ACTIONS_CATALOG if action.category == category]


def get_all_categories() -> List[str]:
    """Get all available action categories."""
    categories = set(action.category for action in MW_ACTIONS_CATALOG)
    return sorted(list(categories))


def search_actions(query: str) -> List[MWAction]:
    """Search actions by name or description."""
    query_lower = query.lower()
    results = []
    for action in MW_ACTIONS_CATALOG:
        if (query_lower in action.action_name.lower() or 
            query_lower in action.display_name.lower() or 
            query_lower in action.description.lower()):
            results.append(action)
    return results
