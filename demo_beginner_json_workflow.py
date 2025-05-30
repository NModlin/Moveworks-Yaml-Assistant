#!/usr/bin/env python3
"""
Beginner-Friendly JSON Data Selection and YAML Generation Demo

This script demonstrates the enhanced JSON selector capabilities
for beginners, showing how to extract data from complex JSON responses
and use it in YAML generation.
"""

import json
from typing import Dict, Any, List


def extract_value_by_path(data: Dict[str, Any], path: str) -> Any:
    """
    Extract value from JSON data using dot notation path.
    
    Supports paths like:
    - data.user_info.name
    - data.tickets[0].title
    - data.user.permissions[1]
    """
    if path.startswith('data.'):
        path = path[5:]  # Remove 'data.' prefix

    # Parse path with array indices support
    parts = []
    current_part = ""
    in_brackets = False
    
    for char in path:
        if char == '[':
            if current_part:
                parts.append(current_part)
                current_part = ""
            in_brackets = True
        elif char == ']':
            if in_brackets and current_part:
                try:
                    parts.append(int(current_part))
                except ValueError:
                    raise ValueError(f"Invalid array index: '{current_part}' must be a number")
                current_part = ""
            in_brackets = False
        elif char == '.' and not in_brackets:
            if current_part:
                parts.append(current_part)
                current_part = ""
        else:
            current_part += char
    
    if current_part:
        parts.append(current_part)

    # Navigate through the data
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise ValueError(f"Cannot navigate to {part} in {type(current)}")
    
    return current


def visualize_json_structure(data: Dict[str, Any], prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> None:
    """Visualize JSON structure in a tree format."""
    if current_depth >= max_depth:
        return
    
    for i, (key, value) in enumerate(data.items()):
        is_last = i == len(data) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if isinstance(value, dict):
            print(f"{prefix}{current_prefix}{key}/ ({len(value)} keys)")
            next_prefix = prefix + ("    " if is_last else "│   ")
            visualize_json_structure(value, next_prefix, max_depth, current_depth + 1)
        elif isinstance(value, list):
            print(f"{prefix}{current_prefix}{key}: [{len(value)} items] 📋")
            if value and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                for j, item in enumerate(value[:2]):  # Show first 2 items
                    item_prefix = "└── " if j == len(value[:2]) - 1 else "├── "
                    if isinstance(item, dict):
                        print(f"{next_prefix}{item_prefix}[{j}]/ ({len(item)} keys)")
                    else:
                        print(f"{next_prefix}{item_prefix}[{j}]: {item}")
                if len(value) > 2:
                    print(f"{next_prefix}    ... and {len(value) - 2} more items")
        else:
            display_value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
            print(f"{prefix}{current_prefix}{key}: {display_value}")


def demo_beginner_workflow():
    """Demonstrate the complete beginner workflow."""
    print("=" * 80)
    print("🎯 BEGINNER-FRIENDLY JSON DATA SELECTION WORKFLOW")
    print("=" * 80)
    print()
    
    # Sample API response (realistic IT service management scenario)
    api_response = {
        "user_lookup": {
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
                }
            ],
            "stats": {
                "total_tickets": 15,
                "open_tickets": 3,
                "closed_tickets": 12,
                "avg_resolution_time": "2.5 days"
            }
        }
    }
    
    print("📊 STEP 1: UNDERSTAND YOUR JSON STRUCTURE")
    print("-" * 50)
    print("Here's your API response structure:")
    print()
    visualize_json_structure(api_response)
    print()
    
    print("🎯 STEP 2: SELECT THE DATA YOU NEED")
    print("-" * 50)
    print("Let's extract specific information for our workflow:")
    print()
    
    # Define what data we want to extract
    data_selections = {
        "User's Full Name": "data.user_lookup.user.name",
        "User's Email": "data.user_lookup.user.email",
        "User's Department": "data.user_lookup.user.department",
        "Manager's Name": "data.user_lookup.user.manager.name",
        "First Permission": "data.user_lookup.user.permissions[0]",
        "Admin Permission": "data.user_lookup.user.permissions[2]",
        "Latest Ticket Title": "data.user_lookup.recent_tickets[0].title",
        "Latest Ticket Status": "data.user_lookup.recent_tickets[0].status",
        "Total Tickets": "data.user_lookup.stats.total_tickets",
        "Open Tickets": "data.user_lookup.stats.open_tickets"
    }
    
    extracted_values = {}
    
    for label, path in data_selections.items():
        try:
            value = extract_value_by_path(api_response, path)
            extracted_values[label] = value
            print(f"✅ {label:20} → {value}")
            print(f"   Path: {path}")
        except Exception as e:
            print(f"❌ {label:20} → Error: {e}")
        print()
    
    print("📋 STEP 3: GENERATE YAML WITH YOUR DATA")
    print("-" * 50)
    print("Now let's create a YAML workflow using the extracted data:")
    print()
    
    # Generate YAML example
    yaml_template = f"""# Generated YAML using selected data paths
action:
  action_name: send_user_summary
  output_key: summary_result
  input_args:
    # User Information
    user_name: {data_selections["User's Full Name"]}
    user_email: {data_selections["User's Email"]}
    department: {data_selections["User's Department"]}
    
    # Manager Information  
    manager_name: {data_selections["Manager's Name"]}
    
    # Permissions
    basic_permission: {data_selections["First Permission"]}
    admin_access: {data_selections["Admin Permission"]}
    
    # Ticket Information
    latest_ticket: {data_selections["Latest Ticket Title"]}
    ticket_status: {data_selections["Latest Ticket Status"]}
    
    # Statistics
    total_tickets: {data_selections["Total Tickets"]}
    open_tickets: {data_selections["Open Tickets"]}
    
    # Composed message using multiple data points
    summary_message: |
      User Summary for {{{{ {data_selections["User's Full Name"]} }}}}
      
      Department: {{{{ {data_selections["User's Department"]} }}}}
      Manager: {{{{ {data_selections["Manager's Name"]} }}}}
      
      Ticket Statistics:
      - Total: {{{{ {data_selections["Total Tickets"]} }}}}
      - Open: {{{{ {data_selections["Open Tickets"]} }}}}
      
      Latest Ticket: {{{{ {data_selections["Latest Ticket Title"]} }}}}
      Status: {{{{ {data_selections["Latest Ticket Status"]} }}}}"""
    
    print(yaml_template)
    print()
    
    print("💡 BEGINNER TIPS & BEST PRACTICES")
    print("-" * 50)
    tips = [
        "🎯 Always test your data paths before using them in YAML",
        "📋 Use array indices [0], [1] to access specific items in lists",
        "🔍 Check if arrays have enough items before accessing high indices",
        "📝 Use descriptive names for your YAML fields",
        "🔄 Remember the format: data.step_output_key.field_name",
        "✅ Validate your generated YAML before deploying",
        "🚀 Start simple and gradually add more complex data selections",
        "📊 Use metadata fields (like stats) for counts and summaries"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    print()
    
    print("🎉 WORKFLOW COMPLETE!")
    print("You've successfully:")
    print("   ✅ Analyzed a complex JSON structure")
    print("   ✅ Selected specific data using paths")
    print("   ✅ Generated YAML with your selected data")
    print("   ✅ Learned best practices for beginners")


if __name__ == "__main__":
    demo_beginner_workflow()
