"""
Tutorial data and sample JSON responses for the Moveworks YAML Assistant tutorials.

This module contains realistic sample data that tutorials use to demonstrate
JSON path selection and workflow creation.
"""

# Sample JSON data for Basic Single-Step Tutorial
BASIC_USER_LOOKUP_JSON = {
    "user": {
        "id": "emp_12345",
        "name": "John Doe",
        "email": "john.doe@company.com",
        "department": "Engineering",
        "location": "San Francisco",
        "manager": {
            "id": "mgr_67890",
            "name": "Jane Smith",
            "email": "jane.smith@company.com"
        },
        "permissions": ["read", "write", "admin"],
        "active": True
    }
}

# Sample JSON data for Advanced Tutorial - User Data
ADVANCED_USER_DATA_JSON = {
    "user": {
        "id": "emp_12345",
        "name": "John Doe",
        "email": "john.doe@company.com",
        "department": "Engineering",
        "location": "San Francisco",
        "manager": {
            "id": "mgr_67890",
            "name": "Jane Smith",
            "email": "jane.smith@company.com"
        },
        "permissions": ["read", "write", "admin"],
        "active": True
    },
    "recent_tickets": [
        {
            "id": "TKT-001",
            "title": "Password Reset Request",
            "status": "open",
            "priority": "high",
            "created": "2024-01-15T09:30:00Z",
            "category": "Account Access"
        },
        {
            "id": "TKT-002",
            "title": "Software Installation - Visual Studio",
            "status": "in_progress",
            "priority": "medium",
            "created": "2024-01-14T14:20:00Z",
            "category": "Software Request"
        },
        {
            "id": "TKT-003",
            "title": "VPN Connection Issues",
            "status": "closed",
            "priority": "low",
            "created": "2024-01-13T11:15:00Z",
            "category": "Network"
        }
    ],
    "preferences": {
        "notification_method": "email",
        "language": "en-US",
        "timezone": "America/Los_Angeles"
    },
    "statistics": {
        "total_tickets": 15,
        "open_tickets": 2,
        "avg_resolution_time": "4.5 hours"
    }
}

# Sample JSON data for Advanced Tutorial - Ticket Creation Response
ADVANCED_TICKET_RESPONSE_JSON = {
    "ticket": {
        "number": "INC0012345",
        "sys_id": "abc123def456",
        "state": "New",
        "short_description": "User access issue",
        "description": "User unable to access critical systems",
        "caller_id": "emp_12345",
        "assigned_to": {
            "id": "tech_789",
            "name": "Tech Support Team",
            "email": "tech@company.com"
        },
        "priority": "2 - High",
        "urgency": "2 - High",
        "impact": "2 - Medium",
        "category": "Access Management",
        "subcategory": "Account Access",
        "created_time": "2024-01-15T10:30:00Z",
        "estimated_resolution": "2024-01-16T18:00:00Z",
        "sla_due": "2024-01-17T10:30:00Z"
    },
    "workflow_status": {
        "stage": "initial_triage",
        "next_actions": ["assign_technician", "escalate_if_urgent"],
        "automation_flags": {
            "auto_assign": True,
            "escalation_eligible": True,
            "requires_approval": False
        }
    },
    "related_data": {
        "similar_tickets": [
            {
                "number": "INC0012340",
                "similarity_score": 0.85,
                "resolution": "Password reset resolved issue"
            }
        ],
        "knowledge_articles": [
            {
                "id": "KB001234",
                "title": "Troubleshooting Account Access Issues",
                "relevance_score": 0.92
            }
        ]
    }
}

# Sample script code for tutorials
BASIC_SCRIPT_EXAMPLE = """# Extract user information
user_name = data.user_info.user.name
user_email = data.user_info.user.email
user_dept = data.user_info.user.department

# Create a greeting message
greeting = f"Hello, {user_name}!"
summary = f"User {user_name} from {user_dept} department"

# Return processed data
return {
    "greeting": greeting,
    "user_name": user_name,
    "user_email": user_email,
    "summary": summary
}"""

ADVANCED_SCRIPT_EXAMPLE = """# Extract data from multiple sources
user_name = data.user_data.user.name
user_dept = data.user_data.user.department
user_location = data.user_data.user.location
ticket_number = data.ticket_result.ticket.number
recent_ticket_count = len(data.user_data.recent_tickets)
open_tickets = data.user_data.statistics.open_tickets

# Analyze user's ticket history
high_priority_tickets = [
    ticket for ticket in data.user_data.recent_tickets 
    if ticket.priority == "high"
]

# Create comprehensive analysis
analysis = {
    "user_profile": {
        "name": user_name,
        "department": user_dept,
        "location": user_location,
        "ticket_history_count": recent_ticket_count,
        "current_open_tickets": open_tickets
    },
    "current_ticket": {
        "number": ticket_number,
        "created_for": user_name,
        "assigned_to": data.ticket_result.ticket.assigned_to.name
    },
    "risk_analysis": {
        "is_repeat_user": recent_ticket_count > 3,
        "has_high_priority_tickets": len(high_priority_tickets) > 0,
        "priority_user": user_dept in ["Engineering", "Sales", "Executive"],
        "escalation_recommended": open_tickets > 2
    },
    "recommendations": {
        "auto_assign": data.ticket_result.workflow_status.automation_flags.auto_assign,
        "escalate": data.ticket_result.workflow_status.automation_flags.escalation_eligible,
        "priority_handling": user_dept in ["Engineering", "Sales"]
    }
}

return analysis"""

# Tutorial step validation data
TUTORIAL_VALIDATIONS = {
    "basic_single_step": {
        "action_name": "mw.get_user_by_email",
        "output_key": "user_info",
        "script_output_key": "greeting_result",
        "expected_paths": [
            "data.user_info.user.name",
            "data.user_info.user.email",
            "data.user_info.user.department"
        ]
    },
    "advanced_compound_action": {
        "user_action_name": "mw.get_user_by_email",
        "user_output_key": "user_data",
        "ticket_action_name": "servicenow.create_incident",
        "ticket_output_key": "ticket_result",
        "script_output_key": "comprehensive_analysis",
        "switch_condition": "data.user_data.recent_tickets[0].priority == 'high'",
        "expected_paths": [
            "data.user_data.user.name",
            "data.user_data.recent_tickets[0].priority",
            "data.ticket_result.ticket.number",
            "data.user_data.statistics.total_tickets"
        ]
    }
}

# Tutorial completion criteria
TUTORIAL_COMPLETION_CRITERIA = {
    "basic_single_step": {
        "min_steps": 2,
        "required_step_types": ["action", "script"],
        "required_json_parsing": True,
        "required_path_selection": True
    },
    "advanced_compound_action": {
        "min_steps": 4,
        "required_step_types": ["action", "action", "switch", "script"],
        "required_json_parsing": True,
        "required_path_selection": True,
        "required_conditional_logic": True,
        "required_multi_source_data": True
    }
}

def get_tutorial_json_data(tutorial_id: str, step_type: str = "user"):
    """Get sample JSON data for a specific tutorial and step type."""
    # Handle unified tutorial system IDs
    if tutorial_id in ["basic_single_step", "interactive_basic", "unified_interactive_basic", "user_lookup", "basic_example"]:
        return BASIC_USER_LOOKUP_JSON
    elif tutorial_id in ["advanced_compound_action", "unified_module_1_basic"]:
        if step_type == "user":
            return ADVANCED_USER_DATA_JSON
        elif step_type == "ticket":
            return ADVANCED_TICKET_RESPONSE_JSON
    return {}

def get_tutorial_script_example(tutorial_id: str):
    """Get sample script code for a specific tutorial."""
    # Handle unified tutorial system IDs
    if tutorial_id in ["basic_single_step", "interactive_basic", "unified_interactive_basic", "unified_module_1_basic"]:
        return BASIC_SCRIPT_EXAMPLE
    elif tutorial_id in ["advanced_compound_action"]:
        return ADVANCED_SCRIPT_EXAMPLE
    return "# Enter your script code here\nreturn {}"

def validate_tutorial_progress(tutorial_id: str, workflow_data: dict) -> dict:
    """Validate tutorial progress against expected criteria."""
    criteria = TUTORIAL_COMPLETION_CRITERIA.get(tutorial_id, {})
    validations = TUTORIAL_VALIDATIONS.get(tutorial_id, {})
    
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "progress": 0
    }
    
    # Add validation logic here based on criteria
    # This would be implemented to check workflow structure
    
    return results
