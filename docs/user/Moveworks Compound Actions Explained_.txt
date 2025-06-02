Understanding Moveworks Compound Actions for YAML Generator Development
Moveworks Compound Actions serve as a powerful mechanism for developers to orchestrate multiple, distinct operations into a single, cohesive automation. Their primary purpose is to enable the execution of complex tasks by combining various elements such as input data definitions, individual system interactions (like HTTP calls or script executions), and control flow logic to manage the sequence and conditions of these operations.1 This capability is fundamental for building sophisticated automations within the Moveworks platform.
The role and implementation of Compound Actions have evolved. In versions of the Plugin Workspace prior to April 2025, Compound Actions were a mandatory component for any plugin, even those intending to use only a single action. Developers would create a Compound Action and then "promote" it to a Plugin to make it accessible to end-users via the bot. However, in Plugin Workspace versions post-April 2025, Compound Actions are no longer a strict requirement for plugins. They can be incorporated as part of a plugin through "Action Activities" but are not essential if a plugin only needs a single action or if action chaining is handled directly within the plugin's logic.1
This evolution signifies a shift in their recommended usage. Post-April 2025, Compound Actions are particularly advised for scenarios where developers aim to chain together a series of actions to accomplish a well-defined, workflow-focused task within an Action Activity. In this context, Compound Actions are seen as less "intelligent" in a conversational sense and more geared towards executing predefined sequences. For more dynamic, conversational experiences where the Moveworks AI Assistant needs to follow intricate business processes and engage in multi-turn interactions with users, chaining actions directly within a plugin is often the preferred approach.1 Understanding this distinction is crucial when designing a YAML generator, as the optimal structure and use of Compound Actions will depend on the intended behavior of the automation.
Core Components and Architecture
Moveworks Compound Actions are constructed from several key building blocks that, when combined, enable the automation of complex processes. These core components are defined within the YAML structure and dictate the behavior and data flow of the automation.
At the heart of a Compound Action are its Input Variables. These define the data that the workflow requires to execute successfully. Essentially, they form the contract for what information must be supplied to the Compound Action when it is invoked.1 For example, a Compound Action designed to provision software might require input variables such as the user's email and the name of the software to be provisioned.
The actual work within a Compound Action is performed by Individual Actions. These can take several forms 1:
* HTTP calls: These allow the Compound Action to interact with external systems via their APIs, sending requests and receiving responses. This is fundamental for integrating with various enterprise applications.
* APIthon Scripts: For more complex logic, data manipulation, or computations that are not easily achieved through simple HTTP calls or built-in functionalities, developers can embed APIthon (a Python-based scripting language) directly within the Compound Action.
* Built-in Actions: Moveworks provides a library of pre-defined actions for common operations within the platform, such as creating approval requests or sending notifications. These built-in actions simplify development by encapsulating common platform interactions.
To manage the execution of these individual actions and implement sophisticated logic, Compound Actions utilize Control Flow Logic. This includes 1:
* Conditionals: Often implemented using a switch expression, these allow the Compound Action to make decisions and execute different sets of actions based on specific criteria or data values.
* Loops: Typically implemented using a for expression, these enable the Compound Action to iterate over a collection of items and perform actions for each item.
* Return: This allows the Compound Action to gracefully conclude its execution and, optionally, pass data back to the calling context or to the user.
* Other control flow mechanisms like try_catch for error handling and raise for explicitly signaling errors are also available.
The interplay of these components—defining necessary inputs, executing various types of actions, and controlling the execution path with logic—allows Compound Actions to model and automate a wide array of business processes. A YAML generator designed to create Compound Actions must therefore be capable of accurately representing each of these component types and their interrelationships within the generated YAML.
YAML for Compound Actions: Syntax, Expressions, and Best Practices
YAML serves as the primary authoring language for defining Moveworks Compound Actions.3 The structure of this YAML is critical, as it dictates the sequence of operations, data flow, and conditional logic. A thorough understanding of its syntax and expressive capabilities is essential for any tool that aims to generate or process these definitions. The comprehensive suite of expressions available in YAML effectively transforms it from a mere data serialization format into a declarative language for defining these intricate workflows.
A central element in multi-step Compound Actions is the steps key. When a Compound Action involves multiple actions or expressions, these must be encapsulated as a list under the steps key. This defines a clear order of execution.2 For single-expression Compound Actions, the steps key is optional.
Key YAML Expressions
Compound Actions support a variety of expressions, each serving a specific function in the workflow:


Expression
	Key Fields
	Purpose/Function
	YAML Syntax Snippet Example (Conceptual)
	Relevant Source(s)
	action
	action_name (mandatory), output_key (mandatory), input_args, progress_updates, delay_config
	Executes HTTP requests or native (built-in) Moveworks actions.
	action:<br/>action_name: get_user_details<br/>output_key: user_info<br/>input_args:<br/>user_id: data.employee_id
	2
	script
	code (mandatory), output_key (mandatory), input_args
	Executes custom APIthon (Python) code for complex logic or data manipulation.
	script:<br/>` code: \
	<br/> # python code here<br/> return data.input_list.upper()<br/> output_key: processed_data<br/> input_args:<br/> input_list: data.raw_items`
	switch
	cases (mandatory, list of condition and steps), default (optional)
	Implements conditional logic (if/else if/else or switch/case). Executes steps under the first true condition.
	switch:<br/>cases:<br/>- condition: data.user_role == "admin"<br/>steps: [...]<br/>- condition: data.user_role == "editor"<br/>steps: [...]<br/>default:<br/>steps: [...]
	2
	for
	each (mandatory), index (mandatory), in (mandatory), output_key (mandatory), steps
	Iterates over a collection (list/array), executing defined steps for each item.
	for:<br/>each: item<br/>index: idx<br/>in: data.item_collection<br/>output_key: loop_results<br/>steps: [...]
	2
	parallel
	for (for loop structure) OR branches (list of steps), output_key (if using for)
	Executes multiple expressions or loop iterations concurrently.
	parallel:<br/>branches:<br/>- steps: [...]<br/>- steps: [...]
	2
	return
	output_mapper (optional)
	Gracefully ends the Compound Action and can map data to a structured output.
	return:<br/>output_mapper:<br/>final_message: "Process complete"<br/>details: data.action_result
	2
	raise
	output_key (mandatory), message (optional)
	Stops the Compound Action by explicitly raising an error.
	raise:<br/>output_key: critical_error<br/>message: "Invalid input detected"
	2
	try_catch
	try (mandatory, with steps), catch (mandatory, with steps), on_status_code (optional)
	Implements error handling. Executes catch block if an error occurs in try block.
	try_catch:<br/>try:<br/>steps: [...]<br/>catch:<br/>on_status_code:<br/>steps: [...]
	2
	YAML Authoring Specifics and Best Practices
Several YAML authoring conventions are critical for Moveworks Compound Actions:
* Multi-line Inputs for Scripts: When defining script actions with multi-line APIthon code, a vertical bar (|) must follow the code: key. This ensures the YAML parser correctly interprets the entire block of code.3
YAML
script:
 code: |
   # Line 1 of script
   # Line 2 of script
   #...

* DSL Escaping for Constants: The Moveworks Data Mapper language, used for input_args and other dynamic value expressions, parses all inputs as DSL strings. Consequently, numeric and boolean literal values must be enclosed in single quotes.3 For instance:
YAML
input_args:
 count: '10'        # Integer literal
 is_enabled: 'true' # Boolean literal
 pi_value: '3.14159' # Decimal literal

* YAML Literal Quoting: Due to YAML's own syntax rules, string, list, and object constants used as values within the Data Mapper language often require an additional layer of quoting or the use of YAML's block quote syntax (>) for clarity and correctness.3
   * Using double quotes: string_value: '"my string"'
   * Using block quote:
YAML
list_value: >
 [1, 2, "abc"]
object_value: >
 {"key": "value", "count": 123}

The meticulous nature of these quoting and escaping rules means that a YAML generator must be precise to avoid syntax errors or misinterpretation by the Moveworks platform.
      * Handling Missing Fields from HTTP Actions: A common integration challenge arises when fields expected from an HTTP action's response are missing. This often occurs if the action's "Output Schema," defined in Agent Studio, does not accurately reflect all fields present in the actual API response. To resolve this, the Output Schema for the specific HTTP action must be updated in Agent Studio to include all relevant fields. Agent Studio provides a "Generate From Response" feature to help automate this schema creation.3 While a YAML generator might not directly modify Agent Studio configurations, it's important for developers using the generator to be aware that the behavior of an action step is tied to this external schema definition.
      * Absence of Comments: Notably, YAML comments (#) are not supported within the Moveworks live editor for Compound Actions and will be removed upon saving.2 For developing and maintaining complex Compound Actions that require explanatory comments, it is recommended to save the YAML definitions as local files or manage them using a version control system like Git, where comments can be preserved. This lack of inline commenting in the platform itself places a higher emphasis on clear output_key naming and logical structuring within the YAML for maintainability.
The detailed specifications for YAML syntax and data handling underscore the need for a YAML generator to be more than a simple template filler; it must function as a "code generator" for this domain-specific workflow language, ensuring adherence to all syntactic and semantic rules.
Data Handling and the Compound Action Data Bank
Effective data management is crucial for the functioning of Compound Actions. Moveworks provides a "Compound Action Data Bank," a runtime environment that holds all relevant data accessible during the execution of a Compound Action. This data bank is primarily accessed through a few key top-level objects.5
Central Data Access Keys
      * data: This is the most frequently used key and acts as the central repository for dynamic data. It's a dictionary that contains:
      * Input Variables: The resolved values of Input Variables defined for the Compound Action are placed here at the start of execution. They are accessed using the syntax data.{{input_variable_name}}.5 For example, if an Input Variable ticket_id is defined, it can be referenced as data.ticket_id.
      * Expression Outputs: The results from completed expressions (such as action, script, or for loops) that have an output_key defined are stored under this key. These are accessed as data.{{output_key}}.5 For instance, the result of an action with output_key: user_details would be available as data.user_details. This data object serves as the primary mechanism for state management and data propagation throughout the Compound Action's lifecycle. Actions and scripts read their inputs from it and write their outputs back to it, enabling a chain of operations.
      * meta_info (and requestor): These keys provide contextual information, primarily about the user who initiated the Compound Action.
      * meta_info.user: Contains various attributes of the current user, such as meta_info.user.first_name, meta_info.user.email_addr, and meta_info.user.role.5 A comprehensive list of available user attributes can be referenced in the Moveworks documentation.
      * requestor: This key is also mentioned as containing user information, with fields accessible via requestor.<field_name> (e.g., requestor.email_addr).6 It's likely that meta_info.user and requestor provide access to similar, if not identical, sets of user data. The availability of rich user context through these keys allows Compound Actions to be personalized and to execute logic that is contextually relevant to the individual invoking the automation.
      * mw: This key provides access to the suite of Moveworks Native (Built-in) Actions. For example, a built-in action to create an approval can be invoked using mw.create_generic_approval_request as the action_name in an action step.6
Data Flow Mechanics
The flow of data within a Compound Action follows a clear pattern:
      1. Input Variables, once resolved, populate the data object.
      2. Each action, script, or control flow expression (like for) that specifies an output_key writes its result to data.{{output_key}} upon successful completion.6
      3. Subsequent steps in the Compound Action can then access these results from the data object to use as their own inputs, effectively creating a data pipeline.4 A practical example involves an action get_user_device storing its output in data.device, which is then used by a subsequent action via input_args: { device_id: data.device.asset_uuid }.5
Structure of output_key Data
The structure of the data stored under an output_key depends on the expression that produced it:
      * For an action or script, the output_key typically holds the direct result, such as a JSON object returned by an API or a value computed by the script.
      * For for loop expressions, the output_key associated with the loop itself stores a list of dictionaries. Each dictionary in this list corresponds to one iteration of the loop. Furthermore, each of these dictionaries contains entries for the output_keys of all steps that were executed within that specific iteration.5 This nested structure is critical for correctly accessing data produced inside loops. For example, to access a field id from an incident_manager_profile object (which was the output of a step inside a loop) for a particular iteration (identified by index), the reference might look like data.outage_ticket_process_results[index].incident_manager_profile.id.5 A YAML generator must be capable of constructing such indexed paths when referencing data from loop iterations.
Input and Output Mappers
While not directly part of the Compound Action YAML syntax itself, the concept of mappers is relevant when Compound Actions are used within "Action Activities" (the post-April 2025 model).
      * Input Mapper: An Action Activity can define an Input Mapper, typically using JSON Bender, to transform and map data (from user-provided slots or outputs of previous Activities) to the Input Variables expected by the Compound Action it invokes.8
      * Output Mapper: Similarly, an Action Activity can have an Output Mapper to define the structure of its output, which can be derived from the data returned by the Compound Action. This allows for "dot-walking" into the Compound Action's return object or using advanced Bender for more complex transformations.8 The documentation also alludes to input and output mappers in the general context of Compound Actions for sophisticated data manipulation beyond Python primitives, suggesting internal capabilities or design considerations for data transformation.6
Additional Data Bank Fields
For advanced scenarios, particularly for monitoring and debugging, the data bank may expose other fields 6:
      * workflow_id: A unique identifier for the specific instance of the Compound Action execution.
      * statuses: A mapping of step identifiers to their execution status (e.g., PENDING, COMPLETE, ERROR).
      * pending_data: Data from expressions that are currently in a PENDING state.
      * error_data: Information about errors encountered by steps that are in ERROR or ERROR_HANDLED states.
      * progress_updates: A list of progress messages that have been sent to the user during the Compound Action's execution.
Understanding these data handling mechanisms, particularly the role of the data object and the structure of outputs from different expressions, is fundamental for a YAML generator to produce correct and functional Compound Action definitions.
Understanding 'Slots' vs. 'Input Variables' in Compound Actions
In the Moveworks ecosystem, the terms 'Slots' and 'Input Variables' both refer to data inputs but are used in slightly different contexts, particularly concerning Compound Actions. Clarifying their distinction and relationship is important for understanding the overall data flow into a Compound Action.
Definition of 'Input Variables' (Compound Action Context):
Input Variables are explicitly defined as part of a Compound Action's configuration within the Plugin Workspace, typically under an "Input fields tab".1 They represent the specific data elements that the Compound Action workflow itself requires to execute its defined steps. These Input Variables form the internal data contract for the Compound Action. For example, a Compound Action designed to create a JIRA ticket might define Input Variables such as summary, description, and project_key. Within the Compound Action's YAML, these are accessed via the data object, e.g., data.summary.
Definition of 'Slots' (Plugin/User Interaction Context):
Slots are described as input values that a plugin needs to successfully execute.10 They are the primary mechanism by which the Moveworks AI Assistant collects information from the end-user (e.g., through conversation) or retrieves it from its memory (e.g., from previous conversational turns). Slots are configured at the plugin or Action Activity level and can have various properties, including data types (e.g., string, integer, User object), validation policies, inference policies (whether to infer from context or always ask), and resolver strategies (how to obtain or disambiguate slot values).10 Examples include a ticket_id slot for a plugin that closes JIRA tickets, or channel_name and new_name slots for a plugin that renames a Slack channel.10
Relationship and Data Flow:
The relationship between Slots and Input Variables has evolved with the Moveworks platform:
      * Agent Studio (Classic - Pre-April 2025): In this older model, when a Compound Action was "promoted" to become a Plugin, its defined Input Variables implicitly became the Slots for that Plugin.10 There wasn't a distinct layer of slot configuration separate from the Compound Action's input definition.
      * Plugin Workspace (Post-April 2025) & Action Activities: In the current model, when a Compound Action is utilized within an "Action Activity," the distinction is clearer:
      1. Slots are defined at the Action Activity level. These are what the AI Assistant attempts to fill by interacting with the user or context.
      2. The Input Variables are defined within the Compound Action itself.
      3. An Input Mapper within the Action Activity configuration bridges the gap. This mapper takes the values collected for the Action Activity's Slots (and potentially outputs from previous activities) and maps them to the Input Variables expected by the Compound Action.8 The documentation explicitly states, "You can configure Slots by adding Input Variables when setting up your Compound Action" 9, directly linking the definition of a Compound Action's Input Variables to how its required inputs (effectively, slots) are configured when it's integrated into the Plugin Workspace.
Essentially, Input Variables define the "API contract" for what data a Compound Action needs internally. Slots, on the other hand, represent the "user interface" or plugin-level mechanism for gathering that data. This separation, especially in the Action Activity model, promotes the reusability of Compound Actions. A single Compound Action (with its defined Input Variables) could theoretically be used by multiple Action Activities, each with different Slot configurations or data sources feeding into those Input Variables.
Data Types:
Both Slots and the Input Variables they map to support a consistent set of data types. These include primitive types like str (string), int (integer), float (decimal number), bool (boolean), as well as a special User type. The User type is significant because it represents a Moveworks User object, containing a rich set of attributes for that user, rather than just a simple string like an email address. Lists of these types (e.g., List[str], List[User]) are also supported, allowing for multiple values to be passed.9
For a YAML generator, the primary concern is the definition and usage of Input Variables within the Compound Action's YAML (e.g., data.my_input_variable). However, the developer using the generated YAML must understand how these Input Variables will ultimately be populated from Slots configured at a higher level (e.g., in an Action Activity).
Practical Examples and Use Cases of Compound Actions
The practical application of Compound Actions is best understood through examples. The Moveworks documentation provides several YAML snippets that illustrate how different expressions and data handling techniques are combined to achieve specific automation goals. These examples serve as valuable blueprints for constructing new Compound Actions and for a YAML generator to learn structural patterns.
Detailed Walkthrough of Provided YAML Examples
The following examples showcase common patterns in Compound Action YAML 4:


Example Name
	Primary Goal
	Key YAML Constructs Demonstrated
	Input Variables (Slots)
	Key Output/Return
	Source(s)
	Get Salesforce Accounts by Name
	Fetch SFDC account details.
	Single action step, input_args mapping, progress_updates, return with output_mapper.
	account_name
	description, account_id from SFDC.
	4
	Create Salesforce Case & Sync to JIRA
	Create SFDC case, create JIRA issue, update SFDC case.
	Sequential action steps, chaining output_keys to input_args, $CONCAT for string manipulation.
	description, subject, account_id, type
	Implicitly, the final state of updated SFDC case.
	4
	Onboard Users
	Onboard users across Azure, JIRA, Okta with conditional group addition.
	Multiple action steps, IF...THEN...ELSE NULL and $CONCAT in input_args, switch statement for conditional logic.
	username, firstName, lastName, companyName, groupName, managerName, managerEmail
	lastName, firstName (mapped from inputs).
	4
	Lookup Gcal Events
	Fetch Google Calendar events and clean the data using a script.
	action step (UUID action name), script action with Python list comprehension, input_args from previous action's output.
	start_date, end_date
	final_events (cleaned list of GCal events).
	4
	Get Salesforce Accounts by Name (Single Action, Return):
This Compound Action takes an account_name as input. Its YAML consists of a single action step (get_account_info) where data.account_name is mapped to the action's input_args. It includes progress_updates to inform the user. A return step then uses an output_mapper to extract specific fields like description and account_id from the result of the action (e.g., data.account_info.records.Description).4 The data flows from the input account_name to the get_account_info action, whose output is stored in account_info, and then selected fields are returned.
Create Salesforce Case & Sync to JIRA (Multi-Action):
This example demonstrates a sequence of three action steps: create_sfdc_case, create_jira_issue, and update_sfdc_case. It takes description, subject, account_id, and type as inputs for the Salesforce case creation. The output of the first action (data.case_info.id) and the second action (data.jira_issue.key) are then used as inputs for the third action, showcasing data chaining. The $CONCAT function is used in input_args to construct the JIRA link.4
Onboard Users (Multi-Action, Switch, Return):
A more complex workflow, this Compound Action uses username, firstName, lastName, companyName, groupName, managerName, and managerEmail as inputs. It involves multiple action steps to interact with Azure, JIRA, and Okta. It utilizes conditional logic with IF... THEN... ELSE NULL and string concatenation with $CONCAT directly within input_args. A key feature is a switch statement that checks data.groupName; if present, it executes additional steps to add the user to an Azure group.4 This illustrates how inputs can control branching logic.
Lookup Gcal Events (Action, Script Action, Return):
This example combines an action (identified by a UUID as action_name) to fetch Google Calendar events based on start_date and end_date, followed by a script action. The script takes the items from the calendar output (data.gcal_output.items) as its input. Its code field contains a Python list comprehension to process and transform this data into cleaned_events. Finally, a return step maps data.cleaned_events to the output.4 This highlights the use of scripting for custom data manipulation.
These examples provide concrete templates for how a YAML generator should structure various types of Compound Actions, from simple single-action calls to multi-step, conditional workflows with custom scripting.
Common IT Automation Use Cases
While the documentation doesn't always explicitly link Compound Actions to high-level IT use cases, the capabilities described lend themselves well to automating common IT processes.12 The procedural nature of many IT tasks, involving sequences of steps, conditional logic, and interactions with multiple systems, aligns well with the structure of Compound Actions.
      * Software Provisioning (e.g., Tableau Access):
A Compound Action for software provisioning could take user_email and software_name as Input Variables. Steps might include:
         1. An action using mw.get_user_by_email to fetch user details.
         2. An action (custom HTTP) to check existing licenses or group memberships.
         3. A switch statement based on eligibility:
         * If eligible and license available: an action to add the user to a provisioning group (e.g., via MS Graph API for Azure AD) and an action using mw.send_plaintext_chat_notification to confirm access.
         * If approval is needed: an action using mw.create_generic_approval_request sent to the user's manager.
         * If not eligible: a raise expression to indicate an error.
         4. A return step to provide a status message.
         * Hardware Troubleshooting (e.g., Citrix VDI Reset):
Based on troubleshooting logic described for Citrix VDI issues 12, a Compound Action could:
            1. Take user_email as an Input Variable.
            2. Use mw.get_user_by_email to get the user_record_id.
            3. (Optionally) An action (custom HTTP) to query the user's assigned VDI if not known.
            4. An action (HTTP) to the Citrix Director API to reboot the VDI session.
            5. A delay_config on a subsequent action to wait for the reboot.
            6. An action (HTTP) to check the VDI status post-reboot.
            7. A switch based on status: if OK, notify user of success; otherwise, notify of failure and potentially trigger a ticket creation action.
These conceptual applications demonstrate how the structural elements of Compound Actions (actions, inputs, conditionals, outputs) can be mapped to real-world IT automation scenarios. A sophisticated YAML generator could even offer templates based on these common patterns.
Built-in Actions in Compound Actions
Moveworks provides a suite of "Built-in Actions" (also referred to as Native Actions) that can be directly invoked from within Compound Actions. These actions encapsulate common platform functionalities, simplifying development and ensuring consistent interaction with Moveworks services.7 Their use can significantly accelerate the creation of Compound Actions for typical enterprise tasks.
Referencing Mechanism
Built-in actions are referenced within an action step of a Compound Action by using the action_name prefix mw. followed by the specific name of the built-in action.7
For example:


YAML




action:
 action_name: mw.create_generic_approval_request
 #... other action fields

Key Examples and Their Parameters
The following table details some commonly used built-in actions and their essential parameters 7:


Built-in Action (action_name)
	Description
	Key Input Parameters (Name, Type, Required/Optional)
	Typical output_key Content
	Source(s)
	mw.create_generic_approval_request
	Creates an in-bot Moveworks approval request. Plugin continues if answered within 30 days.
	approval_key (string, Opt), approvers (List[User], Opt, overrides key), approval_details (string, Req), users_requested_for (List[User], Req)
	Information about the created approval request.
	7
	mw.generate_structured_value_action
	Calls an LLM to produce structured output based on a JSON schema.
	payload (object, Req), output_schema (object, Req), system_prompt (string, Opt), strict (boolean, Opt), model (string, Opt)
	The structured object generated by the LLM.
	7
	mw.generate_text_action
	Calls an LLM for standard text generation.
	user_input (string, Req), system_prompt (string, Opt), model (string, Opt)
	The generated text string.
	7
	mw.send_plaintext_chat_notification
	Sends a chat notification to a specified user.
	user_record_id (string, Req - obtained via user lookup), message (string, Req)
	Status of the notification attempt.
	7
	mw.batch_get_users_by_email
	Retrieves multiple Moveworks user records by their email addresses.
	user_emails (List[string], Req)
	A list of User objects.
	7
	mw.get_user_by_email
	Retrieves a single Moveworks user record by email, including all attributes.
	user_email (string, Req)
	A single User object.
	7
	An important consideration for actions like mw.create_generic_approval_request is that parameters expecting user information (e.g., approvers, users_requested_for) require full Moveworks User objects, not just email strings. These User objects are typically retrieved using other built-in actions like mw.get_user_by_email or mw.batch_get_users_by_email.7 This often leads to a common pattern in Compound Actions: first, an action to look up user(s) by email (perhaps obtained from meta_info.user or an Input Variable), and then a subsequent action that uses the retrieved User object(s).
For LLM-based built-in actions (mw.generate_structured_value_action, mw.generate_text_action), it's noted that GovCloud customers might need to specify a model like "gpt-3.5-turbo-0125" if the default (e.g., GPT-4o) is not supported in their environment.7
Other Platform Action Types
While not directly "built-in actions" callable via the mw. prefix within Compound Action YAML, the broader Moveworks platform supports other types of actions, often presented as solutions at the end of a Path in conversational AI design. These include presenting ingested knowledge base answers, text responses, forms, executing generic APIs (which are configured as HTTP actions), and smart handoffs to human agents.13 Compound Actions can play a role in workflows that ultimately lead to one of these outcomes, for instance, by gathering necessary data or performing backend operations before a form is presented or a handoff is initiated.
The availability of these built-in actions simplifies many common integration and notification tasks, allowing developers to focus on the unique logic of their automation rather than on the boilerplate of interacting with core Moveworks services. A YAML generator should be aware of these common mw. actions and their parameters to facilitate their inclusion in generated Compound Actions.
Error Handling and Debugging in Compound Actions
Robust error handling and effective debugging strategies are essential for creating reliable Compound Actions. The Moveworks platform provides built-in mechanisms within the YAML syntax for managing errors, and understanding common pitfalls can prevent issues during development and deployment.
Built-in Error Handling Mechanisms
The Compound Action YAML syntax includes expressions specifically designed for error management 2:
            * try_catch Expression: This is the primary tool for proactive error handling.
            * The try block contains a list of steps (actions, scripts, etc.) that might potentially fail during execution.
            * If an error occurs within any step in the try block, execution transfers to the catch block.
            * The catch block also contains steps that define how to respond to the error. This could involve logging the error, sending a notification, attempting a recovery action, or returning a specific error message.
            * An optional on_status_code field within the catch block allows developers to specify which types of errors (e.g., HTTP status codes like 400 or 502, or custom error strings from raise expressions) should trigger this particular catch. If on_status_code is omitted, the catch block will handle any error originating from the try block. This structure enables graceful recovery from failures and allows for alternative execution paths, preventing abrupt termination of the entire Compound Action.
            * raise Expression: This expression is used to explicitly stop the Compound Action and signal an error condition.
            * It includes a mandatory output_key where error information will be stored.
            * An optional message field allows for a custom error message to be defined, which can be useful for logging or user feedback. The raise expression is valuable for scenarios like input validation failure or when an unrecoverable state is detected within the workflow.
The inclusion of these first-class error handling expressions in the YAML syntax signifies that building resilient automations is an expected design principle, not merely an afterthought. A YAML generator should facilitate the inclusion of try_catch blocks, especially around action steps involving external HTTP calls, which are common points of failure.
Accessing Error Information
When errors occur, information about them can often be found within the Compound Action Data Bank 6:
            * error_data: This key holds information about errors from steps that have entered an ERROR or ERROR_HANDLED state.
            * statuses: This mapping provides the execution status (e.g., UNKNOWN, PENDING, COMPLETE, ERROR, ERROR_HANDLED, CANCELLED) for each step ID within the Compound Action, allowing for inspection of which specific steps failed.
Common YAML and Configuration Pitfalls
Several common issues can arise from incorrect YAML syntax or configuration 3:
            * Multi-line script errors: Forgetting the | character after code: in script actions can lead to parsing failures for multi-line scripts.
            * DSL Escaping errors: Numeric and boolean constants within DSL expressions (e.g., in input_args) must be quoted (e.g., count: '10', is_active: 'true'). Omitting these quotes can cause misinterpretation.
            * YAML literal quoting issues: Incorrectly quoting string, list, or object literals can lead to YAML parsing errors. Using the block quote syntax (>) can sometimes simplify the management of quotes for complex literals.
            * Missing fields from HTTP Action responses: This occurs if the "Output Schema" defined for an HTTP Action in Agent Studio doesn't match the actual API response. The resolution is to update the Output Schema in Agent Studio to accurately reflect all fields returned by the API.3
Gateway and System-Level Errors
Failures within Compound Actions can also stem from issues in underlying systems or gateways 14:
            * Gateway Errors: Integrations often pass through a gateway, which may return standardized error codes like 400 INPUT_VALIDATION_FAILED, 401 AUTHENTICATION_FAILED, 404 NOT_FOUND, or 502 EXTERNAL_REST_ERROR. HTTP actions within a Compound Action might receive these.
            * LDAP/Agent Errors: Problems with backend services, such as LDAP authentication failures (e.g., error code 52e for invalid credentials, 775 for account locked out), SSL certificate issues (e.g., unknown CA (560)), or network timeouts due to WAFs or throttling of ITSM systems, can cause actions within a Compound Action to fail.
Debugging Strategies and Recommendations
Moveworks suggests several practices for testing and debugging plugins and, by extension, Compound Actions 16:
            * Test Authentically: Use realistic input values during testing, as artificial inputs like "TEST" may not accurately model user behavior and can confuse the AI agent.
            * Clear History Often: If repeatedly testing the same plugin or Compound Action, the AI agent might perceive it as unreliable and stop executing it. Clearing chat history can mitigate this.
            * Use Logs: The Moveworks platform provides comprehensive logging capabilities that are invaluable for diagnosing where a plugin or Compound Action might be misbehaving.
            * Consult common error troubleshooting guides and the developer community for solutions to known issues.
Distinguishing between errors in the YAML definition itself (which prevent parsing or correct interpretation) and runtime errors (which occur during execution) is important. A YAML generator should primarily focus on producing syntactically valid YAML that avoids common pitfalls. However, it should also generate YAML that incorporates robust runtime error handling using try_catch and raise to ensure that, when failures do occur, they are managed gracefully and provide sufficient information for debugging via logs and the data bank.
Advanced Patterns, Limitations, and Best Practices
Beyond the fundamental syntax and error handling, several advanced patterns, platform limitations, and best practices shape the effective design and implementation of Moveworks Compound Actions.
Advanced Data Flow Patterns
            * Chaining Actions: A core pattern is the sequential execution of actions where the output of one action, stored in its output_key and accessible via data.{{output_key}}, serves as an input for a subsequent action.5 This allows for building complex data processing pipelines.
            * Discarding Unneeded Output: If the result of a particular action or script is not required by any subsequent steps in the Compound Action, it's good practice to assign its output_key to an underscore (_), e.g., output_key: _.6 This signals that the output is intentionally not used, improving the readability and maintainability of the YAML.
Limitations and Constraints
Several limitations can influence how and when Compound Actions are used:
            * Asynchronous Nature in Action Activities (Post-April 2025): A significant characteristic in the modern Plugin Workspace is that Compound Actions, when used within an "Action Activity," operate asynchronously. This means they do not return data directly back to the calling step of the Plugin in a synchronous manner that would allow the Plugin to immediately use that data to continue a conversational flow.8 Instead, Compound Actions in this context typically provide "progress updates" back to the user while they execute in the background. This asynchronicity makes them suitable for tasks that can run independently but less so for situations where a plugin requires an immediate, multi-step computed result to make its next conversational decision.
            * Resolver Strategy Limitations: Dynamic methods within Resolver Strategies, which are used for advanced, dynamic lookup of possible slot values during user interaction, currently cannot use Compound Actions. The recommendation is to use HTTP Actions for such dynamic lookups.17 This restricts the use of Compound Actions in the specific context of sophisticated slot-filling mechanisms.
            * Rate Limits: Moveworks, like most platforms, imposes rate limits on integrations with chat systems (e.g., Slack, Microsoft Teams) and on its own APIs (e.g., the Events API).18 Compound Actions that perform a high volume of external HTTP calls or heavily utilize platform APIs must be designed with these rate limits in mind. While individual actions can have a delay_config 2, comprehensive handling of rate limit responses (like HTTP 429 errors) might require sophisticated try_catch logic or design patterns that distribute load over time, though the platform's native retry mechanisms for chat integrations offer some resilience.18
Best Practices
            * Citation Configuration for User Trust: When a Compound Action returns data that will be presented to the user and needs to be verifiable (e.g., search results, ticket details), it's crucial to configure the return step's output_mapper to support citations. This greatly improves user trust in the AI agent.19
            * For a list of citable objects, return them under a results key: {"results":}.
            * For a single citable object, return it under a result key: {"result": {"id": "INC-456", "friendly_id": "Incident Subject"}}.
            * Each citable object must have a string-based id field. It may also have an optional string-based friendly_id.
            * The id should be unique and unlikely to appear organically in the bot's textual response to ensure correct anchoring of the citation link.19 A YAML generator creating Compound Actions that fetch citable data must be capable of producing these specific return structures.
            * Idempotency (Implied Best Practice): While not explicitly mandated for Compound Actions in the provided materials, actions that modify external systems (e.g., creating a ticket, updating a user record) should ideally be designed to be idempotent. This means that if the action is executed multiple times with the same inputs, it produces the same result without unintended side effects (e.g., creating duplicate records). This is particularly important if a Compound Action might be retried due to transient errors.
            * Modularity and Single Responsibility: Design Compound Actions to perform a specific, well-defined task or sub-process. This enhances their reusability across different plugins or scenarios and makes them easier to test, debug, and maintain. Overly complex Compound Actions that try to do too many unrelated things can become difficult to manage.
Understanding these advanced patterns, limitations, and best practices is key to leveraging Compound Actions effectively and avoiding common pitfalls in automation design on the Moveworks platform. The asynchronous nature of Compound Actions within the newer Action Activity framework is a particularly critical factor to consider when architecting solutions.
Conclusion and Key Takeaways for YAML Generator Development
The development of a YAML generator for Moveworks Compound Actions requires a deep understanding of their structure, syntax, data handling mechanisms, and operational context within the Moveworks platform. This document has detailed these aspects to provide a comprehensive foundation for such a tool, particularly for an AI coding assistant tasked with its creation or refinement.
Key Takeaways for the YAML Generator:
            1. Mastery of YAML Structure and Expressions:
            * The generator must accurately produce the steps list for sequential execution.
            * It needs to correctly generate all core YAML expressions: action, script, switch, for, parallel, return, raise, and try_catch, including all their mandatory and optional fields with correct data types.
            * Adherence to YAML-specific syntax is critical: using | for multi-line scripts, correctly quoting constants for DSL escaping (e.g., 'true', '123'), and managing YAML's own literal quoting rules for strings, lists, and objects.
            2. Understanding Core Data Flow Principles:
            * The data object is the central state container. The generator must manage the lifecycle of data from Input Variables (accessed as data.{{input_variable_name}}), through output_keys of intermediate steps (written to data.{{output_key}}), to input_args of subsequent steps or the final return expression.
            * References to user context via meta_info.user (or requestor) and built-in actions via mw. must be correctly formatted.
            * The specific nested structure of for loop outputs (a list of dictionaries, where each dictionary holds the outputs of that iteration's steps) must be handled correctly when generating references to data produced within loops.
            3. Incorporating Best Practices and Handling Limitations:
            * The generator should facilitate robust error handling by making it easy to include try_catch blocks, especially around action steps involving external calls.
            * It should be aware of the syntax for raise to allow for explicit error signaling.
            * For Compound Actions returning citable data, the generator must produce the specific results or result key structure in the return step's output_mapper, including id and friendly_id fields.
            * The generator (or the AI assistant guiding its use) should be mindful of the asynchronous nature of Compound Actions when used in modern Action Activities, as this impacts how they can be integrated into larger plugin flows.
Recommendations for the AI Coding Assistant:
To effectively assist in developing or fixing the YAML generator, the AI assistant should leverage the information in this report to:
            * Perform Schema Validation: Validate generated YAML against the implicit schemas of Compound Action expressions detailed (e.g., mandatory fields for action, structure of switch cases).
            * Recognize and Suggest Patterns: Identify common workflow patterns (e.g., fetch-process-notify, conditional branching based on user data) and suggest appropriate YAML structures or templates.
            * Promote Error Handling: Encourage or automatically include try_catch blocks for operations prone to failure, and guide the correct use of raise.
            * Analyze Data Flow: Help trace the intended flow of data through Input Variables and output_keys to identify potential breaks, incorrect references, or scope issues.
            * Maintain Awareness of Limitations: Understand contexts where a Compound Action might not be the optimal solution (e.g., due to asynchronicity if a synchronous result is needed by a plugin) and potentially suggest alternatives if the user's broader intent is discernible.
            * Utilize Knowledge of Built-in Actions: Be familiar with common mw. actions and their parameters to assist in generating these steps accurately.
            * Emphasize Clarity and Maintainability: Given the lack of comments in the live editor, guide the generation of YAML that is as self-documenting as possible through clear naming of output_keys, logical structuring, and adherence to best practices like using output_key: _ for unused results.
By internalizing these details, the AI coding assistant can significantly contribute to the creation of a robust and accurate YAML generator, enabling developers to more efficiently build powerful automations using Moveworks Compound Actions.
Works cited
            1. Compound Actions - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/compound-actions
            2. Compound Action Reference - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/compound-action-syntax-reference
            3. Troubleshooting Compound Actions - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/saving-compound-actions
            4. Compound Action Examples - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/compound-action-examples
            5. Compound Action Data Bank - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/compound-action-exposed-data
            6. Compound Action Exposed Data - Moveworks, accessed June 1, 2025, https://developer.moveworks.com/creator-studio/reference/compound_actions_data/
            7. Built-in Actions - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/built-in-actions
            8. Activities - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/activities
            9. Slot Types - Moveworks, accessed June 1, 2025, https://developer.moveworks.com/creator-studio/conversation-design/slots/slot-types/
            10. Slots - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/slots
            11. Compound Action Examples - Moveworks, accessed June 1, 2025, https://developer.moveworks.com/creator-studio/reference/compound_actions_examples/
            12. Selecting IT Use Cases - Moveworks Developers, accessed June 1, 2025, https://developer.moveworks.com/creator-studio/program-management/selecting-it-use-cases/
            13. Action Types - AI Agent Marketplace - Moveworks, accessed June 1, 2025, https://developer.moveworks.com/creator-studio/conversation-design/actions/action-types/
            14. Errors - Moveworks, accessed June 1, 2025, https://help.moveworks.com/reference/errors
            15. Moveworks Agent Troubleshooting Guide, accessed June 1, 2025, https://help.moveworks.com/docs/moveworks-agent-troubleshooting
            16. Testing & Debugging - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/help
            17. Resolver Strategies - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/resolver-strategies
            18. Integration Rate Limits - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/moveworks-product-rate-limits-chat-systems-apis-etc
            19. Citation Configuration - Moveworks, accessed June 1, 2025, https://help.moveworks.com/docs/citation-configuration