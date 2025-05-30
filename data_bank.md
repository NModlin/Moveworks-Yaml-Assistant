Compound Action Data Bank
Suggest Edits
When you're building your Compound Action, you can reference additional variables which will be provided by Moveworks when the Compound action executes. This is the Compound Action Data Bank.

meta_info
You can access the meta_info key from any part of the Compound Action. It's structure takes the following form.

JSON

{			
	"meta_info": {
		"user": { ... }
  }
}
meta_info.user
We can access the user attributes of the current user (the one who invoked the plugin) with the following notation meta_info.user.{{attribute}}. View all of the available user attributes here.

YAML

steps:
  - action:
      action_name: some_action
      output_key: some_action_resp
      input_args:
        name: meta_info.user.first_name
  - return:
      output_mapper:
        name: meta_info.user.first_name
        role: meta_info.user.role
        department: meta_info.user.department
        some_attr: meta_info.user.custom_data.some_attr
data
You can access the data key from any part of the Compound Action. It's structure takes the following form.

json

{			
	"data": {
    ...input_variable_names,
    ...output_keys
  }
}
data.{{input_variable_name}}
Your Compound Action's Input Variables are inserted at the top level of the data key. So for example, if you defined 2 input variables (name & age)...


You could reference it in your Compound Action as data.name and data.age

yaml

- return:
    output_mapper:
      name: data.name
      age: data.age
data.{{output_key}}
Expressions "save" their data to an output key so you can reference them later. Some expressions that utilize output keys include

Actions (Built-in, HTTP, etc.)
For expressions
Raise expressions
These keys can be accessed using the notation data.{{output_key}}, facilitating data flow and handling within the compound action.

action Example
In this example, we pass data through the output key from one action to the next.

YAML

steps:
  - action:
      action_name: get_user_device
      output_key: device
      input_args:
        user_email: meta_info.user.email_addr
  - action:
      action_name: clean_recycle_bin_on_device
      output_key: remote_action_result
      input_args:
        device_id: data.device.asset_uuid # data.device is the output key of the first action
for Example
When you use a for expression, the output keys of all steps within that for expression are inserted into the for expression's output_key as a list of dictionaries.

For example, if you had the following compound action...

YAML

steps:
	- action:
  		action_name: get_open_outages
      output_key: outage_tickets
      # Assume response structure is [ {"ticket_id": "OUT-123", ...}, {"ticket_id": "OUT-456", ...}, ... ]
  - for:
  		each: ticket
      index: index
      in: data.outage_tickets
      output_key: outage_ticket_process_results
      steps:
        - action:
            action_name: get_incident_manager_for_outage
            input_args:
            	outage_id: ticket.system_id
            output_key: incident_manager_profile
            # Assume response structure is { "id": "7bd99d76-d5a6-4ed9-bea5-7f513bf35c6a", "status": "INACTIVE" }
        - action:
        		action_name: update_incident_manager_profile
            input_args:
            	manager_id: data.outage_ticket_process_results[index].incident_manager_profile.id
              status: "ON_CALL"
            output_key: updated_manager_profile            

The resulting data bank under data will look like this:

JSON

{
  "data": {
    "outage_tickets": [ {"ticket_id": "OUT-123", ...}, {"ticket_id": "OUT-456", ...}, ... ]
    "outage_ticket_process_results": [
      {
        // Process results for "OUT-123"
        "incident_manager_profile": { "id": "7bd99d76-d5a6-4ed9-bea5-7f513bf35c6a", "status": "INACTIVE" },
        "updated_manager_profile":  { "id": "7bd99d76-d5a6-4ed9-bea5-7f513bf35c6a", "status": "ON_CALL" }
      },
      {
        // Process results for "OUT-456"
        "incident_manager_profile": { "id": "839b82da-38f2-41f4-91ec-db70de7c3c56", "status": "INACTIVE" },
        "updated_manager_profile":  { "id": "839b82da-38f2-41f4-91ec-db70de7c3c56", "status": "ON_CALL" }
      }
  	]
  },
  ...
} 