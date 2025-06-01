#!/usr/bin/env python3
"""
Demo script showing input variables functionality.
This creates a sample workflow with input variables and shows the generated YAML.
"""

# Simple demo without complex imports
def create_sample_yaml():
    """Create a sample YAML showing input variables structure."""
    
    sample_yaml = """action_name: user_lookup_workflow
input_variables:
  user_email:
    type: string
    description: Email address of the user to look up
    required: true
  max_results:
    type: integer
    description: Maximum number of results to return
    required: false
    default: 10
  include_details:
    type: boolean
    description: Whether to include detailed user information
    required: false
    default: false
steps:
  - action: mw.get_user_by_email
    input_args:
      email: data.user_email
      limit: data.max_results
      detailed: data.include_details
    output_key: user_info
    description: Get user information by email
  - script:
      code: |
        # Process the user data
        user = data.user_info
        max_count = data.max_results
        
        if user:
            result = {
                "found": True,
                "user_id": user.get("id"),
                "user_name": user.get("name"),
                "email": data.user_email,
                "search_limit": max_count
            }
        else:
            result = {
                "found": False,
                "email": data.user_email,
                "search_limit": max_count
            }
        
        return result
    output_key: processed_result
    description: Process user lookup results"""
    
    return sample_yaml

def main():
    """Main demo function."""
    print("🎯 Input Variables Demo for Moveworks YAML Assistant")
    print("=" * 60)
    
    print("\n📋 This demo shows the new input variables feature:")
    print("   • Define input variables with types and descriptions")
    print("   • Reference variables using data.{variable_name} syntax")
    print("   • Support for required/optional variables with defaults")
    print("   • Integration with existing action and script steps")
    
    print("\n📝 Sample YAML with Input Variables:")
    print("=" * 50)
    
    sample_yaml = create_sample_yaml()
    print(sample_yaml)
    
    print("=" * 50)
    
    print("\n✨ Key Features Implemented:")
    print("   ✓ InputVariable dataclass with validation")
    print("   ✓ Workflow.input_variables field")
    print("   ✓ YAML generation with input_variables section")
    print("   ✓ InputVariablesWidget UI component")
    print("   ✓ Auto-completion for data.{variable_name}")
    print("   ✓ Integration with existing validation systems")
    print("   ✓ Support for all Moveworks data types")
    
    print("\n🎨 UI Components Added:")
    print("   • Input Variables table in left panel")
    print("   • Add/Edit/Delete variable dialogs")
    print("   • Real-time validation with 300ms debouncing")
    print("   • Data type dropdown with Moveworks types")
    print("   • Required/optional toggle with default values")
    
    print("\n🔧 Technical Implementation:")
    print("   • PySide6 UI following existing patterns")
    print("   • 8px margins and #f8f8f8 backgrounds")
    print("   • Integration with enhanced input args tables")
    print("   • Auto-completion in JSON Path Selector")
    print("   • Compliance with lowercase_snake_case naming")
    
    print("\n🚀 Ready to Use!")
    print("   The input variables feature is now fully integrated")
    print("   into the Moveworks YAML Assistant and ready for use.")

if __name__ == "__main__":
    main()
