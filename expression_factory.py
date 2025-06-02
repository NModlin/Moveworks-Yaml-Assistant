"""
Expression Factory for the Moveworks YAML Assistant.

This module provides a factory class that simplifies expression creation with sensible defaults,
making it easier for users to create workflows without needing to understand all the technical details.
"""

from typing import Dict, Any, List, Optional
from core_structures import (
    ActionStep, ScriptStep, SwitchStep, ForLoopStep, ParallelStep, 
    ReturnStep, RaiseStep, TryCatchStep, SwitchCase, DefaultCase,
    ParallelBranch, CatchBlock
)


class ExpressionFactory:
    """Factory for creating expression instances with sensible defaults."""
    
    @staticmethod
    def create_action(action_name: str = "", output_key: str = "action_result", 
                     input_args: Optional[Dict[str, Any]] = None,
                     description: str = "") -> ActionStep:
        """
        Create an action expression with minimal required fields.
        
        Args:
            action_name: Name of the action to execute
            output_key: Key to store the action result
            input_args: Arguments to pass to the action
            description: Optional description of the action
            
        Returns:
            ActionStep instance with sensible defaults
            
        Example:
            action = ExpressionFactory.create_action(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                input_args={"email": "data.user_email"}
            )
        """
        return ActionStep(
            action_name=action_name,
            output_key=output_key,
            input_args=input_args or {},
            description=description
        )
    
    @staticmethod
    def create_script(code: str = "# Your APIthon code here\nreturn {}", 
                     output_key: str = "script_result",
                     description: str = "") -> ScriptStep:
        """
        Create a script expression with minimal required fields.
        
        Args:
            code: APIthon code to execute
            output_key: Key to store the script result
            description: Optional description of the script
            
        Returns:
            ScriptStep instance with sensible defaults
            
        Example:
            script = ExpressionFactory.create_script(
                code="return {'processed': True}",
                output_key="processing_result"
            )
        """
        return ScriptStep(
            code=code,
            output_key=output_key,
            description=description
        )
    
    @staticmethod
    def create_switch(description: str = "Conditional logic", 
                     cases: Optional[List[SwitchCase]] = None,
                     default_case: Optional[DefaultCase] = None) -> SwitchStep:
        """
        Create a switch expression with minimal required fields.
        
        Args:
            description: Description of the switch logic
            cases: List of switch cases
            default_case: Default case if no conditions match
            
        Returns:
            SwitchStep instance with sensible defaults
            
        Example:
            switch = ExpressionFactory.create_switch(
                description="Handle user access level",
                cases=[
                    SwitchCase(
                        condition="data.user.access_level == 'admin'",
                        steps=[ExpressionFactory.create_action("admin_action")]
                    )
                ]
            )
        """
        return SwitchStep(
            description=description,
            cases=cases or [],
            default_case=default_case
        )
    
    @staticmethod
    def create_for_loop(each: str = "item", in_source: str = "data.items",
                       output_key: str = "loop_results", 
                       steps: Optional[List] = None,
                       description: str = "Process items in loop") -> ForLoopStep:
        """
        Create a for loop expression with minimal required fields.
        
        Args:
            each: Variable name for current item
            in_source: Data path to iterate over
            output_key: Key to store loop results
            steps: Steps to execute for each item
            description: Description of the loop
            
        Returns:
            ForLoopStep instance with sensible defaults
            
        Example:
            for_loop = ExpressionFactory.create_for_loop(
                each="user",
                in_source="data.users",
                output_key="processed_users",
                steps=[ExpressionFactory.create_action("process_user")]
            )
        """
        return ForLoopStep(
            each=each,
            in_source=in_source,
            output_key=output_key,
            steps=steps or [],
            description=description
        )
    
    @staticmethod
    def create_parallel(description: str = "Parallel execution",
                       branches: Optional[List[ParallelBranch]] = None) -> ParallelStep:
        """
        Create a parallel expression with minimal required fields.
        
        Args:
            description: Description of parallel execution
            branches: List of parallel branches
            
        Returns:
            ParallelStep instance with sensible defaults
            
        Example:
            parallel = ExpressionFactory.create_parallel(
                description="Run actions in parallel",
                branches=[
                    ParallelBranch(
                        name="branch1",
                        steps=[ExpressionFactory.create_action("action1")]
                    )
                ]
            )
        """
        return ParallelStep(
            description=description,
            branches=branches or []
        )
    
    @staticmethod
    def create_return(output_mapper: Optional[Dict[str, Any]] = None,
                     description: str = "Return workflow result") -> ReturnStep:
        """
        Create a return expression with minimal required fields.
        
        Args:
            output_mapper: Mapping of output data
            description: Description of the return
            
        Returns:
            ReturnStep instance with sensible defaults
            
        Example:
            return_step = ExpressionFactory.create_return(
                output_mapper={"result": "data.final_result"},
                description="Return final workflow result"
            )
        """
        return ReturnStep(
            output_mapper=output_mapper or {},
            description=description
        )
    
    @staticmethod
    def create_raise(message: str = "An error occurred", 
                    output_key: str = "error_result",
                    description: str = "Raise error") -> RaiseStep:
        """
        Create a raise expression with minimal required fields.
        
        Args:
            message: Error message to raise
            output_key: Key to store error information
            description: Description of the error
            
        Returns:
            RaiseStep instance with sensible defaults
            
        Example:
            raise_step = ExpressionFactory.create_raise(
                message="User not found",
                output_key="user_error"
            )
        """
        return RaiseStep(
            message=message,
            output_key=output_key,
            description=description
        )
    
    @staticmethod
    def create_try_catch(try_steps: Optional[List] = None,
                        catch_block: Optional[CatchBlock] = None,
                        description: str = "Try-catch error handling") -> TryCatchStep:
        """
        Create a try-catch expression with minimal required fields.
        
        Args:
            try_steps: Steps to execute in try block
            catch_block: Catch block for error handling
            description: Description of error handling
            
        Returns:
            TryCatchStep instance with sensible defaults
            
        Example:
            try_catch = ExpressionFactory.create_try_catch(
                try_steps=[ExpressionFactory.create_action("risky_action")],
                catch_block=CatchBlock(
                    steps=[ExpressionFactory.create_raise("Action failed")]
                )
            )
        """
        return TryCatchStep(
            try_steps=try_steps or [],
            catch_block=catch_block,
            description=description
        )


class CommonPatterns:
    """Common workflow patterns using the expression factory."""

    @staticmethod
    def user_lookup_pattern(email_field: str = "data.user_email") -> List:
        """Create a common user lookup pattern."""
        return [
            ExpressionFactory.create_action(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                input_args={"email": email_field},
                description="Look up user by email"
            ),
            ExpressionFactory.create_script(
                code="""
# Validate user lookup result
if hasattr(data.user_info, 'user') and data.user_info.user:
    return {
        "success": True,
        "user_id": data.user_info.user.id,
        "user_name": data.user_info.user.name
    }
else:
    return {
        "success": False,
        "error": "User not found"
    }
                """.strip(),
                output_key="user_validation",
                description="Validate user lookup result"
            )
        ]

    @staticmethod
    def error_handling_pattern(action_name: str, input_args: Dict[str, Any]) -> TryCatchStep:
        """Create a common error handling pattern."""
        return ExpressionFactory.create_try_catch(
            try_steps=[
                ExpressionFactory.create_action(
                    action_name=action_name,
                    output_key="action_result",
                    input_args=input_args
                )
            ],
            catch_block=CatchBlock(
                steps=[
                    ExpressionFactory.create_script(
                        code="""
return {
    "success": False,
    "error": "Action failed",
    "message": "Please try again or contact support"
}
                        """.strip(),
                        output_key="error_response"
                    )
                ]
            ),
            description="Execute action with error handling"
        )

    @staticmethod
    def conditional_processing_pattern(condition: str, true_action: str, false_action: str) -> SwitchStep:
        """Create a common conditional processing pattern."""
        return ExpressionFactory.create_switch(
            description="Conditional processing based on condition",
            cases=[
                SwitchCase(
                    condition=condition,
                    steps=[
                        ExpressionFactory.create_action(
                            action_name=true_action,
                            output_key="true_result"
                        )
                    ]
                )
            ],
            default_case=DefaultCase(
                steps=[
                    ExpressionFactory.create_action(
                        action_name=false_action,
                        output_key="false_result"
                    )
                ]
            )
        )
