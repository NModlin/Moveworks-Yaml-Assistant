Compound Action Reference
Suggest Edits
The steps Key
The steps key is used to define a sequence of actions or expressions that are executed in order. This key is particularly important in compound actions that involve multiple steps, ensuring that each action is carried out in the correct sequence and allowing for complex logic to be implemented cleanly and efficiently.

When to use the steps Key
Single Expression Compound Action: For Compound Actions that only contain a single action or expression, using the steps key is optional. The action can be specified directly at the top level of the compound action definition.
Multiple Expressions Compound Action: When a Compound Action includes multiple actions or expressions, encapsulating them within a steps list under the steps key is required. This clearly defines the execution order and groups the expressions logically.
Syntax and Examples
Single Expression Without steps:

YAML

action:
  action_name: example_action_name
  output_key: _
  input_args:
    example_input: "Example Value"
Multiple Expressions With steps:

YAML

steps:
  - action:
      action_name: example_action_1_name
      output_key: _
      input_args:
        example_input_1: "Example Value 1"
  - action:
      action_name: example_action_2_name
      output_key: _
      input_args:
        example_input_2: "Example Value 2"
📘
Comments

Currently comments are not supported in the YAML syntax, and will get removed on save. If you require comments, Moveworks recommend saving your compound action as a local YAML file or using a version control system like Github.

Expressions
action (Execute HTTP Requests or Native Actions)
Description: Actions are fundamental tasks the bot can perform, like creating a ticket or searching for a user. They are the basic capabilities that allow the bot to interact with external systems or perform operations.

Schema:

YAML

action:
  action_name: ACTION_NAME
  output_key: OUTPUT_VARIABLE
  input_args:
    input1: INPUT_VARIABLE_1
    input2: INPUT_VARIABLE_2
  delay_config:
    unit1: NUMBER_EXPRESSION
    unit2: NUMBER_EXPRESSION
  progress_updates:
    on_pending: PENDING_MESSAGE_STRING
    on_complete: COMPLETION_MESSAGE_STRING
Fields:

action_name: The unique identifier for the action to be executed.
Type: str (action name)
Mandatory: Yes
output_key: A variable to store the result of the action.
Type: any
Mandatory: Yes
input_args: A dictionary mapping input arguments to their values, allowing for dynamic inputs to the action.
Type: dictionary {} - Accepts Moveworks Data Mapping Syntax
Mandatory: No
progress_updates: An object containing messages to update the user on the action's progress, including messages for pending and completed states.
Type: dictionary {on_pending: text, on_complete: text}
Mandatory: No
delay_config: An object describing how long the Compound Action should wait before executing this action.
Type: dictionary of DSL expressions that return numbers for each unit of time (e.g. "5"):
YAML

milliseconds: "DSL_EXPRESSION"
seconds: "DSL_EXPRESSION"
minutes: "DSL_EXPRESSION"
hours: "DSL_EXPRESSION"
days: "DSL_EXPRESSION"
Mandatory: No
Example Usage 1:

YAML

action:
  action_name: fetch_user_details # Example action_name for fetching user details
  output_key: user_details
  input_args:
    user_id: data.user_id # Assuming user_id is stored in data
  delay_config:
  	seconds: "10" # Wait 10 seconds to execute the action
  progress_updates:
    on_pending: "Fetching user details, please wait..."
    on_complete: "User details fetched successfully."
This action fetches user details based on a given user ID. While the action is in progress, it informs the user that their request is being processed. Once completed, it confirms the successful retrieval of user details.

Additionally, the API response will be stored in the user_details variable, ready for use in subsequent steps of the Compound Action.

Result:

YAML

user_details: {
  "user_id": "abc123",
  "user_name": "John Doe",
  "email": "john.doe@example.com"
}
script (Execute Scripts)
Description: The script expression allows users to write and execute custom code within the compound action, offering a flexible way to perform complex operations or data manipulations. This is particularly useful for tasks that require custom logic or processing that isn't covered by standard actions.

Supported Languages: APIthon (Python)

Schema:

YAML

script:
  code: "input_var_1 + input_var_2"
  input_args:
    input_var_1: INPUT_ARG_VALUE_1
    input_var_2: INPUT_ARG_VALUE_2
  output_key: SCRIPT_RESULT
Fields:

code: The Python code to be executed.
Type: string
Mandatory: Yes
output_key: A variable to store the result of the script's execution.
Type: any
Mandatory: Yes
input_args: A dictionary mapping input argument variables to their values, allowing for dynamic inputs to the script.
Type: dictionary {} - Accepts Moveworks Data Mapping Syntax
Mandatory: No
Example Usage 1: Clean a list of objects

YAML

script:
  output_key: cleaned_events
  input_args:
    events: data.gcal_output.items
  code: "[{'htmlLink': event.get('htmlLink'), 'description': event.get('description'), 'summary': event.get('summary')} for event in events]"
This compound action takes a list of events and extracts only the htmlLink, description, and summary fields for each event, creating a simplified list of event details.

Result:

YAML

cleaned_events: [
  {
    "htmlLink": "https://example.com/event1",
    "description": "Team meeting",
    "summary": "Discuss project updates"
  },
  {
    "htmlLink": "https://example.com/event2",
    "description": "Client call",
    "summary": "Review contract details"
  }
]
Description: The script processes each event in the input list, extracting the htmlLink, description, and summary fields, and stores the cleaned list of events in cleaned_events.

Example Usage 2: Add two numbers using a script.

YAML

script:
  output_key: addition_result
  input_args:
    a: 1
    b: 2
  code: "a + b"
This Script performs a simple addition of two numbers (1 and 2) and stores the result (3) in additional_result

Result:

YAML

 stats: 3
Example Usage 3: Process a list of numbers and get statistics from the list using a multiline Python script.

YAML

script:
  output_key: stats
  input_args:
    numbers: "[1, 2, 3, 4, 5, 6]"
  code: >
    sum_numbers = sum(numbers);
    count_numbers = len(numbers);
    average = sum_numbers / count_numbers;
    stats = {'sum': sum_numbers, 'count': count_numbers, 'average': average};
    stats
This compound action calculates the sum, count, and average of a list of numbers. It demonstrates how to perform multiple operations within a script, showcasing the use of variables and basic arithmetic operations to compute statistics, which are then stored as a dictionary in stats.

Result:

YAML

stats: {
  "sum": 21,
  "count": 6,
  "average": 3.5
}
 The script calculates the sum (21), count (6), and average (3.5) of the given list of numbers [1, 2, 3, 4, 5, 6] and stores these statistics in a dictionary under stats. This result demonstrates how multi-line Python scripts can be utilized within compound actions to perform complex data processing and aggregation tasks.

switch (Conditional Statements)
Description: The switch expression functions like an if/else or switch/case statement in traditional programming, allowing for multiple conditions to be evaluated. If a condition is true, the compound action will execute the steps defined under that condition. If no conditions are true, the compound action will execute the steps defined under default, if any.

Schema:

YAML

switch:
  cases:
    - condition: BOOLEAN_CONDITION
      steps:
        - EXPRESSION_1
    - condition: SECOND_BOOLEAN_CONDITION
      steps:
        - EXPRESSION_1
        - EXPRESSION_2
  default:
    steps:
      - EXPRESSION_2
Fields:

cases: A sequence of conditions and their corresponding steps to execute.
Type: list[dict] where each dict contains:
condition (boolean): The boolean expression to evaluate.
steps (list): The expressions to execute if the condition is true.
Mandatory: Yes
default: Specifies the steps to execute if none of the conditions in cases are true. If omitted, the default behavior is to perform no operation.
Type: dict containing:
steps (list): A list of expressions to execute by default.
Mandatory: No
Example Usage 1:

YAML

switch:
  cases:
    - condition: data.user.record_id == requestor.record_id
      steps: []
  default:
    steps:
      - action:
          action_name: mw.send_plaintext_chat_notification
          output_key: requested_for_notification
          input_args:
            user_record_id: data.user.record_id
            message:
              RENDER():
                template: "Hey {{ data.user.first_name }},\n{{ requestor.full_name }} just added you to the {{ data.group.name }} mailing list. You can now receive emails sent to this group.\nThis request is tracked in {{ data.resolve_ticket.ticket.id }}."
In this example, we check if the record_id from data.user matches the record_id from requestor. If they match, no steps are executed (steps: [] signifies an empty action). However, if the condition is not met (meaning the record_id does not match), the compound action defaults to sending a plaintext chat notification using the send_plaintext_chat_notification native action. The message dynamically includes names and group information, informing the user that they have been added to a mailing list and providing a ticket ID for reference. This example demonstrates how switch can be used for conditional logic and actions within a compound action.

Example Usage 2:

YAML

switch:
  cases:
    - condition: data.user.access_level == 'admin'
      steps:
        - action:
            action_name: send_admin_welcome
            output_key: admin_welcome_notification
            input_args:
              user_id: data.user.id
              message: "Welcome, Admin! You have full access to the admin dashboard."
    - condition: data.user.access_level == 'member'
      steps:
        - action:
            action_name: send_member_welcome
            output_key: member_welcome_notification
            input_args:
              user_id: data.user.id
              message: "Welcome, Member! Explore your member benefits in your profile."
  default:
    steps:
      - action:
          action_name: send_generic_access_notification
          output_key: generic_access_notification
          input_args:
            user_id: data.user.id
            message: "You're set! Start exploring your new account."
This compound action sends different welcome messages based on the user's access level. Admins receive a message about accessing the admin dashboard, members are informed about their benefits, and all other users receive a generic welcome message.

Example usage 3:

YAML

switch:
  cases:
    - condition: data.temperature <= 5
      steps:
        - action:
            action_name: alert_cold_temperature
            output_key: cold_temp_alert
            input_args:
              message: "Alert: Temperature is very cold! Ensure heating systems are operational."
    - condition: data.temperature > 5 and data.temperature <= 25
      steps:
        - action:
            action_name: log_moderate_temperature
            output_key: moderate_temp_log
            input_args:
              message: "Temperature is moderate. No action required."
  default:
    steps:
      - action:
          action_name: alert_high_temperature
          output_key: high_temp_alert
          input_args:
            message: "Alert: High temperature detected! Ensure cooling systems are operational."
This compound action categorizes temperature readings into three categories: Cold (≤ 5°C), Moderate (> 5°C and ≤ 25°C), and Hot (> 25°C). Depending on the category, it triggers different actions: sending alerts for cold and hot temperatures, and logging a message for moderate temperatures.

for (iteration/looping)
Description: The for expression functions as a foreach loop, allowing users to iterate through each element of an iterable. This is particularly useful for executing a set of steps or actions on each item within a collection, such as a list or array.

Schema:

YAML

for:
  each: ITERATED_VARIABLE_NAME
  index: INDEX_OF_ITERABLE_NAME
  in: ITERABLE_VARIABLE_NAME
  output_key: VARIABLE_NAME_2
  steps:
    - EXPRESSION_1
    - EXPRESSION_2
Fields:

each: The variable name that represents the current item in the iteration.
Type: string
Mandatory: Yes
index: The variable name that represents the index of the current item in the iteration.
Type: string
Mandatory: Yes
in: The name of the iterable variable that the loop will iterate over.
Type: string
Mandatory: Yes
output_key: A variable to store the results of the loop's execution.
Type: list[expression]
Mandatory: Yes
steps: The list of compound action expressions to be executed on each element of the loop.
Type: list
Mandatory: No
Example usage 1:

Given the payload:

JSON

{
  "users": [
    {
      "id": "user1",
      "age": 35
    },
    {
      "id": "user2",
      "age": 42
    },
    {
      "id": "user3",
      "age": 29
    }
  ]
}
Implementing the compound action:

YAML

for:
  each: user
  index: user_index
  in: data.users
  output_key: requested_for_notifications
  steps:
    - action:
        action_name: action_1
        output_key: action_1_output
In this compound action, for each user in the list data.users, the specified action (action_1) is executed. The loop iterates over all users, performing the action for each one. The results of these actions are then collected and stored in the variable requested_for_notifications. This example demonstrates how to apply actions to a collection of items, such as sending notifications to a list of users or processing a batch of data records.

Example usage 2: Adjusting User Ages and Sending Notifications

For each user in an array, subtract 10 from their age and then send a notification message with the adjusted age.

Implementing the compound action:

YAML

for:
  each: user
  index: user_index
  in: data.users
  output_key: adjusted_ages_notifications
  steps:
    - script:
        code: "return user['age'] - 10"
        input_args:
          user: user
        output_key: adjusted_age
    - action:
        action_name: send_age_adjustment_notification
        output_key: age_notification_user_index
        input_args:
          user_id: user.id
          message: $CONCAT(["Your adjusted age is", adjusted_age], " ")
In this compound action, we iterate over an array of users, each represented as an object with an age attribute. For each user, the first step is a script that calculates the user's age subtracted by 10. The result of this calculation is stored in the variable adjusted_age.

The second step is an action that sends a notification to each user, informing them of their adjusted age. The message dynamically includes the calculated adjusted_age for each user. The output_key for the notification action includes the user_index to ensure that each notification's output is uniquely identified.

parallel (parallel processing)
Description: Parallel processing enables the execution of multiple expressions concurrently. This feature is essential for optimizing compound actions by allowing independent tasks to run simultaneously, thus reducing the overall execution time.

Schema 1:

YAML

parallel:
  for:
    in: ITERABLE
    index_key: index_key
    output_key: OUTPUT_VARIABLE
    steps:
      - compound action_EXPRESSION_1
      - compound action_EXPRESSION_2
Schema 2:

YAML

parallel:
  branches:
    - steps:
    	- compound action_EXPRESSION_1
    - steps:
    	- compound action_EXPRESSION_2
Fields:

for: Specifies a loop to execute expressions in parallel for each item in an iterable.
Mandatory: No (One of for or branches is required)
Type: For expression
branches: A list of expressions to be executed in parallel.
Mandatory: No (One of for or branches is required)
Type: list
in: The iterable variable name for the for loop.
Mandatory: Yes (if using for)
Type: string
output_key: A variable to store the results of the parallel execution.
Mandatory: Yes (if using for)
Type: string
Example usage 1: Fetching User Details in Parallel

Given a list like the one below:

JSON

{
  "user_ids": ["user1", "user2", "user3"]
}
We can iterate over the list and fetch details for each user in parallel:

YAML

parallel:
  for:
    each: user_id
    in: data.user_ids
    index_key: user_index
    output_key: user_details
    steps:
      - action:
          action_name: fetch_user_details
          output_key: _
          input_args:
            user_id: user_id
Result:

YAML

user_details: [
  { "user_id": "user1", "details": {...} },
  { "user_id": "user2", "details": {...} },
  { "user_id": "user3", "details": {...} }
]
This result shows the details fetched for each user ID, demonstrating the concurrent execution's efficiency.

Example usage 2: Running Multiple Independent Actions in Parallel

YAML

parallel:
  branches:
    - steps:
      - action:
          action_name: log_event
          input_args:
            event_name: "user_login"
    - steps:
      - action:
          action_name: send_email
          input_args:
            email: data.requestor_email
            subject: "Login Notification"
            body: "You have logged in successfully."
‘This compound action concurrently executes two actions: logging an event and sending an email notification. It demonstrates the use of parallel branches to run independent tasks simultaneously.

Result: 
The actions complete concurrently, with no explicit result output due to the nature of the actions (logging and sending an email). This example illustrates improving compound action efficiency by parallelizing independent operations.

return (return a value to chat)
Description: The Return expression ends the compound action without throwing an error. Unlike an error-based exit (handled by a Raise expression), Return exits gracefully, providing a way to output data in a structured format using the output_mapper, which follows the Moveworks Data Mapping Syntax.

🚧
Warning

Be mindful of our token limits (🔗).
Return statements have some reserved keywords for Citations (🔗) (results & result). Please do not use the keyword "result" unless you plan to include an "id" and "friendly_id" (optional) which will create a citation.
Schema:

YAML

return:
  output_mapper:
    key1: MAPPED_VALUE1
    key2: MAPPED_VALUE2
Fields:

output_mapper: A dictionary that represents a mapping between output variables and their values, utilizing Moveworks Data Mapping syntax for structured and typed data transformation.
Mandatory: No
Type: dictionary {} - Accepts Moveworks Data Mapping Syntax
Example usage 1:
Given a previous action statement that looks like this:

YAML

action:
  action_name: abc123abc123abc123abc123
  output_key: action_output
We could have a return statement that returns the output of that action:

YAML

return:
  output_mapper:
      a: data.action_output
Example usage 2: Displaying a List of Users

Given a list of objects like the one below:

JSON

{
  "users": [
    {"id": "user1", "name": "alice", "age": 30},
    {"id": "user2", "name": "bob", "age": 25},
    {"id": "user3", "name": "charlie", "age": 35}
  ]
}
We can return a new list with only the id and name

YAML

return:
  output_mapper:
    MAP():
      converter:
        id: item.id
        name: item.name.$TITLECASE()
      items: data.users
raise
Description: The Raise expression is used to stop a compound action by raising an error, effectively serving as an early exit mechanism when an error condition is met. It's particularly useful for handling situations where the compound action cannot or should not continue due to issues like permissions, invalid data, or other critical errors.

Schema:

YAML

raise:
  output_key: OUTPUT_VARIABLE
  message: ERROR_MESSAGE_STRING
Fields:

output_key: Represents the variable name where the error information will be stored. This can be used to reference the error details within the compound action.
Type: any
Mandatory: Yes
message: The error message that will be displayed or logged when the error is raised. This provides context and details about the error to the user or developer.
Type: string
Mandatory: No
Example usage 1: Permission Check

Give the following payload:

JSON

{
  "user_role": "guest"
}
We can write a switch statement to check if the user's role != "admin"
If this evaluates to true, we want to raise an error.

YAML

switch:
  cases:
    - condition: data.user_role != 'admin'
      steps:
        - raise:
            message: 'This compound action has failed because you do not have permission'
            output_key: auth_error_key
Result: An error is raised, stopping the Compound Action, with the following message:


This compound action has failed because you do not have permission
try_catch
Description: The try_catch expression allows for the execution of a compound action expression with an error handling mechanism. If the try block encounters an error, the catch block is executed, allowing for graceful error handling and recovery. This is particularly useful for managing errors in compound actions where certain actions might fail under known or unknown conditions.

Schema:

YAML

try_catch:
  try:
    steps:
      - compound action_EXPRESSION
  catch:
    on_status_code:
      - STATUS_CODE
    steps:
      - compound action_EXPRESSION_1
      - compound action_EXPRESSION_2
Fields:

try: Contains the expressions to be executed. If an error occurs in any of these expressions, the compound action proceeds to the catch block.
Mandatory: Yes
Type: dict containing:
steps (list): A list of expressions (e.g., actions or compound actions) to attempt to run.
catch: Specifies the actions to take if an error is encountered in the try block.
Mandatory: Yes
Type: dict containing:
on_status_code (list, optional): The specific list of status codes that will trigger the catch block. If omitted, the catch block is triggered by any error.
steps (list): A list of expressions to execute if an error that matches on_status_code is caught.
on_status_code: Determines which errors will trigger the execution of the catch block. Supports specifying a single status code, a list of codes, or a string representation. If not specified, the catch block is triggered by any error encountered in the try block.
Mandatory: No
Type: int/string/array
Example usage 1: Handling a Potential Failure in an Action

YAML

try_catch:
  try:
    steps:
      - action:
          action_name: may_fail_action
          output_key: action_result
  catch:
    on_status_code: [E400]
    steps:
      - action:
          action_name: notify_admin
          output_key: notify_admin_output
          input_args:
            message: "That flakey action is failing again"
            error: error_data.action_result
      - raise:
          output_key: raised_error
          message: "The action has failed. The IT team is aware this is failing for some cases, please be patient. Someone will look at the open ticket."
This compound action attempts to execute an action that may fail (may_fail_action). If the action fails, the compound action checks if the error's status code is E400. If it is, it notifies an admin with details of the failure and it raises a generic error message to inform the user that the issue is known and being addressed.

FAQ
Q: Are comments supported?
A: Comments are currently not supported

