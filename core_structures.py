"""
Core data structures for the Moveworks YAML Assistant.

This module defines the fundamental classes for representing Compound Action workflows,
including ActionStep, ScriptStep, Workflow, and DataContext classes.

Based on Sections 2.1, 2.3, and 11.1 of the Source of Truth Document.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
import json


class DataPathNotFound(Exception):
    """Exception raised when a data path cannot be found in the DataContext."""
    pass


@dataclass
class ActionStep:
    """
    Represents an action step in a Moveworks Compound Action workflow.

    Attributes:
        action_name: The name of the action to execute
        output_key: Key to store the action's output in the data context
        description: Optional description of what this action does
        input_args: Dictionary of input arguments for the action
        progress_updates: Optional progress update configuration
        delay_config: Optional delay configuration
        user_provided_json_output: Raw JSON string provided by user for this action's output
        parsed_json_output: Parsed version of user_provided_json_output
    """
    action_name: str
    output_key: str
    description: Optional[str] = None
    input_args: Dict[str, Any] = field(default_factory=dict)
    progress_updates: Optional[Dict[str, str]] = None
    delay_config: Optional[Dict[str, int]] = None
    user_provided_json_output: Optional[str] = None
    parsed_json_output: Optional[Any] = None

    def __post_init__(self):
        """Parse JSON output if provided."""
        if self.user_provided_json_output and not self.parsed_json_output:
            try:
                self.parsed_json_output = json.loads(self.user_provided_json_output)
            except json.JSONDecodeError:
                # Keep parsed_json_output as None if JSON is invalid
                pass


@dataclass
class ScriptStep:
    """
    Represents a script step in a Moveworks Compound Action workflow.

    Attributes:
        code: The APIthon script code to execute
        output_key: Key to store the script's output in the data context
        description: Optional description of what this script does
        input_args: Dictionary of input arguments for the script
        user_provided_json_output: Raw JSON string provided by user for this script's output
        parsed_json_output: Parsed version of user_provided_json_output
    """
    code: str
    output_key: str
    description: Optional[str] = None
    input_args: Dict[str, Any] = field(default_factory=dict)
    user_provided_json_output: Optional[str] = None
    parsed_json_output: Optional[Any] = None

    def __post_init__(self):
        """Parse JSON output if provided."""
        if self.user_provided_json_output and not self.parsed_json_output:
            try:
                self.parsed_json_output = json.loads(self.user_provided_json_output)
            except json.JSONDecodeError:
                # Keep parsed_json_output as None if JSON is invalid
                pass


@dataclass
class SwitchCase:
    """
    Represents a case within a switch statement.

    Attributes:
        condition: String condition to evaluate (e.g., "data.action1_output.status == 'completed'")
        steps: List of steps to execute if condition is true
    """
    condition: str
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep']] = field(default_factory=list)


@dataclass
class DefaultCase:
    """
    Represents the default case within a switch statement.

    Attributes:
        steps: List of steps to execute if no other conditions match
    """
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep']] = field(default_factory=list)


@dataclass
class SwitchStep:
    """
    Represents a switch control flow step.

    Attributes:
        description: Optional description of the switch step
        cases: List of SwitchCase instances
        default_case: Optional DefaultCase instance
        output_key: Output key for the switch result (usually '_')
    """
    description: Optional[str] = None
    cases: List[SwitchCase] = field(default_factory=list)
    default_case: Optional[DefaultCase] = None
    output_key: str = "_"


@dataclass
class ForLoopStep:
    """
    Represents a for loop control flow step.

    Attributes:
        description: Optional description of the for loop
        each: Variable name for the current item (e.g., "currentUser")
        index: Optional variable name for the current index (e.g., "i")
        in_source: Data path to the array to iterate over (e.g., "data.action1_output.users_array")
        output_key: Output key for the loop results
        steps: List of steps to execute for each iteration
    """
    description: Optional[str] = None
    each: str = ""
    index: Optional[str] = None
    in_source: str = ""
    output_key: str = ""
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep']] = field(default_factory=list)


@dataclass
class ParallelBranch:
    """
    Represents a branch within a parallel execution block.

    Attributes:
        name: Name of the branch (optional)
        steps: List of steps to execute in this branch
    """
    name: Optional[str] = None
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep']] = field(default_factory=list)


@dataclass
class ParallelForLoop:
    """
    Represents a parallel for loop configuration.

    Attributes:
        each: Variable name for the current item
        index_key: Variable name for the current index
        in_source: Data path to the array to iterate over
        output_key: Output key for the parallel loop results
        steps: List of steps to execute for each iteration in parallel
    """
    each: str = ""
    index_key: Optional[str] = None
    in_source: str = ""
    output_key: str = ""
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep']] = field(default_factory=list)


@dataclass
class ParallelStep:
    """
    Represents a parallel execution control flow step.

    Attributes:
        description: Optional description of the parallel step
        branches: List of ParallelBranch instances to execute in parallel (for branches mode)
        for_loop: ParallelForLoop configuration (for parallel for loop mode)
        output_key: Output key for the parallel results (usually '_')
    """
    description: Optional[str] = None
    branches: Optional[List[ParallelBranch]] = None
    for_loop: Optional[ParallelForLoop] = None
    output_key: str = "_"

    def __post_init__(self):
        """Ensure either branches or for_loop is set, but not both."""
        if self.branches is None and self.for_loop is None:
            self.branches = []
        elif self.branches is not None and self.for_loop is not None:
            raise ValueError("ParallelStep cannot have both branches and for_loop set")


@dataclass
class ReturnStep:
    """
    Represents a return statement that ends workflow execution.

    Attributes:
        description: Optional description of the return step
        output_mapper: Dictionary mapping output keys to data paths
        output_key: Output key for the return result (usually '_')
    """
    description: Optional[str] = None
    output_mapper: Dict[str, str] = field(default_factory=dict)
    output_key: str = "_"


@dataclass
class RaiseStep:
    """
    Represents a raise statement that throws an error and halts execution.

    Attributes:
        description: Optional description of the raise step
        message: Error message to raise (optional)
        output_key: Output key for error information
    """
    description: Optional[str] = None
    message: Optional[str] = None
    output_key: str = "_"


@dataclass
class CatchBlock:
    """
    Represents a catch block within a try/catch construct.

    Attributes:
        description: Optional description of the catch block
        on_status_code: Optional list of status codes that trigger this catch block
        steps: List of steps to execute when an error is caught
    """
    description: Optional[str] = None
    on_status_code: Optional[List[str]] = None
    steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep', 'RaiseStep']] = field(default_factory=list)


@dataclass
class TryCatchStep:
    """
    Represents a try/catch block for error handling.

    Attributes:
        description: Optional description of the try/catch step
        try_steps: List of steps to execute in the try block
        catch_block: Catch block to execute if an error occurs
        on_status_code: Optional list of status codes that trigger the catch block
        output_key: Output key for the try/catch result
    """
    description: Optional[str] = None
    try_steps: List[Union['ActionStep', 'ScriptStep', 'SwitchStep', 'ForLoopStep', 'ParallelStep', 'ReturnStep', 'RaiseStep']] = field(default_factory=list)
    catch_block: Optional[CatchBlock] = None
    on_status_code: Optional[List[str]] = None
    output_key: str = "_"


@dataclass
class Workflow:
    """
    Represents a complete Moveworks Compound Action workflow.

    Attributes:
        steps: List of steps (ActionStep, ScriptStep, or control flow step types)
    """
    steps: List[Union[ActionStep, ScriptStep, SwitchStep, ForLoopStep, ParallelStep, ReturnStep, RaiseStep, TryCatchStep]] = field(default_factory=list)


class DataContext:
    """
    Manages the data context for a Moveworks Compound Action workflow.

    This class simulates the 'data' object that tracks input variables and
    output keys from executed steps, as well as meta_info for user context.
    """

    def __init__(self, initial_inputs: Optional[Dict[str, Any]] = None, meta_info: Optional[Dict[str, Any]] = None):
        """
        Initialize the DataContext.

        Args:
            initial_inputs: Dictionary of initial CA input variables
            meta_info: Dictionary containing meta information like user context
        """
        self.initial_inputs = initial_inputs or {}
        self.step_outputs = {}  # Maps output_key -> parsed_json_output
        self.meta_info = meta_info or {
            "user": {
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "email_addr": "john.doe@company.com",
                "record_id": "12345",
                "role": "Employee",
                "department": "Engineering",
                "custom_data": {}
            }
        }

    def add_step_output(self, output_key: str, parsed_json_value: Any) -> None:
        """
        Add a step's output to the data context.

        Args:
            output_key: The output key for the step
            parsed_json_value: The parsed JSON output from the step
        """
        if output_key != '_':  # '_' means unused output
            self.step_outputs[output_key] = parsed_json_value

    def get_data_value(self, path_string: str) -> Any:
        """
        Retrieve a value from the data context using dot notation.
        Supports both 'data.path' and 'meta_info.path' prefixes.

        Args:
            path_string: Path like 'input_var', 'step_output_key.nested_key',
                        'data.input_var', or 'meta_info.user.first_name'

        Returns:
            The value at the specified path

        Raises:
            DataPathNotFound: If the path is invalid
        """
        # Handle meta_info paths
        if path_string.startswith('meta_info.'):
            meta_path = path_string[10:]  # Remove 'meta_info.' prefix
            return self._navigate_path(self.meta_info, meta_path.split('.'), path_string)

        # Handle data paths (with or without 'data.' prefix)
        if path_string.startswith('data.'):
            path_string = path_string[5:]  # Remove 'data.' prefix

        parts = path_string.split('.')

        # Check initial inputs first
        if parts[0] in self.initial_inputs:
            value = self.initial_inputs[parts[0]]
            return self._navigate_path(value, parts[1:], path_string)

        # Check step outputs
        if parts[0] in self.step_outputs:
            value = self.step_outputs[parts[0]]
            return self._navigate_path(value, parts[1:], path_string)

        raise DataPathNotFound(f"Path '{path_string}' not found in data context")

    def is_path_available(self, path_string: str) -> bool:
        """
        Check if a data path is available in the context.

        Args:
            path_string: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        try:
            self.get_data_value(path_string)
            return True
        except (DataPathNotFound, KeyError, IndexError, TypeError):
            return False

    def _navigate_path(self, value: Any, remaining_parts: List[str], original_path: str) -> Any:
        """
        Navigate through nested dictionaries/lists using remaining path parts.

        Args:
            value: Current value to navigate from
            remaining_parts: Remaining parts of the path
            original_path: Original path string for error messages

        Returns:
            The value at the final path

        Raises:
            DataPathNotFound: If navigation fails
        """
        if not remaining_parts:
            return value

        current_part = remaining_parts[0]

        try:
            if isinstance(value, dict):
                next_value = value[current_part]
            elif isinstance(value, list):
                # Handle array indexing
                index = int(current_part)
                next_value = value[index]
            else:
                raise DataPathNotFound(f"Cannot navigate path '{original_path}': {current_part} is not accessible")

            return self._navigate_path(next_value, remaining_parts[1:], original_path)

        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise DataPathNotFound(f"Path '{original_path}' not found: {str(e)}")

    def get_meta_info_paths(self) -> List[str]:
        """
        Get a list of all available meta_info paths.

        Returns:
            List of available meta_info path strings
        """
        paths = []

        def _extract_paths(obj, prefix="meta_info"):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{prefix}.{key}"
                    paths.append(current_path)
                    if isinstance(value, dict):
                        _extract_paths(value, current_path)

        _extract_paths(self.meta_info)
        return paths

    def get_available_paths(self) -> List[str]:
        """
        Get a list of all available top-level paths in the data context.

        Returns:
            List of available path strings including data and meta_info paths
        """
        paths = []
        # Add data paths
        paths.extend([f"data.{key}" for key in self.initial_inputs.keys()])
        paths.extend([f"data.{key}" for key in self.step_outputs.keys()])
        # Add meta_info paths
        paths.extend(self.get_meta_info_paths())
        return paths
