Data Mapper Reference
Suggest Edits
📘
This document highlights the theory of data mapping language used at Moveworks. To view some common examples visit this document

Overview
The Moveworks Data Mapping Language is a concise, domain-specific language crafted to facilitate the transformation and manipulation of data within the Moveworks platform. It offers a suite of operators and functions that enable users to efficiently map, aggregate, and format data according to their requirements. MW Data Mappers' design prioritizes ease of use, empowering users to implement complex data transformations with minimal coding.

In the MW Data Mapper language, paired with MwDSL, accessing and refining payload data is straightforward and user-friendly. For example, to neatly extract and clean the display_value from a ServiceNow ticket:

Example Payload:

JSON

{
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  }
}
Simplified with MW Data Mappers:

JSON
YAML

{
  "number": "number.display_value.$TRIM()",
  "state": "state.display_value.$TRIM()"
}
Outcome:

JSON

{
  "number": "INC12345",
  "state": "Closed"
}
A core concept in the MW Data Mappers is the BenderDefinition, a function for specific operations, like the simple_eval used here. While simple_eval is implicit for its simplicity and frequent use, other functions may require explicit calls. This guide will dive deeper into these functions, making data manipulation with MW Data Mappers intuitive and effective.

Mapper Function Catalog
The Data Mapper syntax unlocks a suite of operations for transforming data. These operations range from simple evaluations to complex list manipulations and conditional logic.

Field-level Operations: Basic operations like simple_eval for pulling values and eval for evaluating expressions.
Structural Operations: Functions for constructing objects (object), arrays (array), and manipulating structure with FLATTEN and MERGE.
List Manipulation: Operations for transforming lists, including MAP, SORT, COALESCE, and FILTER.
Branching: Conditional logic (CONDITIONAL) and lookup operations (LOOKUP) for dynamic data handling.
String Manipulation: Functions like CONCAT for joining strings, RENDER for template rendering, and STRIP_HTML for removing HTML tags.
Field Level Operators
SIMPLE_EVAL
Description: Facilitates the direct extraction or computation of values from the response object in your data. It provides straightforward access to specific fields and supports the evaluation of expressions involving those fields, such as arithmetic operations.

Output Type: The output type depends on the evaluated expression and can be string, number, boolean, etc.

Parameters:

Expression: The DSL expression to be evaluated. This can involve accessing direct fields, performing arithmetic or logical operations on field values. (Type: DSL)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example MW Data Mapping: Extract and Compute
MW Data Mapping:

JSON
YAML

{
  "ticket_number": "number.display_value.$TRIM()",
  "total_impact": "$INTEGER(state.value) + $INTEGER(impact.value)"
}
Expected Result:

JSON

{
  "ticket_number": "INC12345",
  "total_impact": 11
}
In this example, SIMPLE_EVAL is used in two ways:

To extract and trim the display_value of the number field, returning the ticket number as a trimmed string.
To compute the total impact by converting the value of both the state and impact fields from strings to numbers and then adding them together.
EVAL
Description: Performs dynamic DSL expression evaluation, facilitating complex computations and logical operations. It can incorporate custom arguments to modify the evaluation context, allowing for refined data manipulation.

Output Type: Varies based on the expression, including string, number, boolean, etc.

Parameters:

Expression: A DSL expression for evaluation, capable of arithmetic, logical operations, or accessing data. (Type: DSL)
Args: Optional. Custom arguments as key-value pairs that can alter the evaluation, overriding or supplementing the root object's data. (Type: BenderDefinition)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example 1: Simple Arithmetic Operation
MW Data Mapper Mapping:

JSON
YAML

{
  "total_impact": {
    "EVAL()": {
      "expression": "$INTEGER(state.value) + $INTEGER(impact.value)"
    }
  }
}
Expected Result:

JSON

{
  "total_impact": 11
}
This example showcases EVAL performing an arithmetic operation by adding the numeric values of state and impact fields, demonstrating basic computation capabilities.

Example 2: Using Custom Arguments for Calculation
MW Data Mapping:

JSON
YAML

{
  "adjusted_impact": {
    "EVAL()": {
      "expression": "x + y",
      "args": {
        "x": "$INTEGER(state.value)",
        "y": "$INTEGER(impact.value) * 2"
      }
    }
  }
}
Expected Result:

JSON

{
  "adjusted_impact": 15
}
In this scenario, EVAL utilizes custom arguments (x and y) for the calculation. x is the numeric value of state, and y is double the numeric value of impact. This illustrates how custom arguments can be used to perform more complex calculations.

Example 3: Overriding Parent Context
MW Data Mapping:

JSON
YAML

{
  "sum": {
    "EVAL()": {
      "expression": "x + y + z",
      "args": {
        "x": 3,
        "y": 4,
        "z": "$INTEGER(impact.value)"
      }
    }
  }
}
Expected Result:

JSON

{
  "sum": 11
}
Here, by providing a custom context (x and y as constants) and adding fields from the payload response, EVAL does not disregards the original payload values, showcasing its ability to add to the parent context for specific calculations or additions.

Structural Operators
OBJECT {}
Description: Constructs a JSON object, facilitating the organization of data into a structured format. It inherently supports nesting and allows for the specification of complex paths as keys, enabling the creation of deeply nested objects directly within mappers.

Output Type: object

Parameters:

Children: Specifies the structure and content of the object to be created. Keys represent field names or nested paths, and values define how to populate these fields using various MW Data Mapper definitions. (Type: map<string, BenderDefinition>)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example MW Data Mapping: Structuring Nested Data
MW Data Mapping:

JSON
YAML

{
  "ticket_info": {
    "ticket_number": "number.display_value",
    "ticket_state": "state.display_value",
    "details": {
      "created_by": "sys_created_by.display_value",
      "created_on": "sys_updated_on.display_value",
      "impact_level": "impact.display_value"
    }
  },
  "action_on_reject": "upon_reject.display_value"
}
Expected Result:

JSON

{
  "ticket_info": {
    "ticket_number": "INC12345",
    "ticket_state": "Closed",
    "details": {
      "created_by": "kmok",
      "created_on": "2015-03-10 04:00:07",
      "impact_level": "4 - Localized"
    }
  },
  "action_on_reject": "Cancel all future Tasks"
}
In this example, the OBJECT functionality is implicitly used to create a structured JSON object named ticket_info, which includes nested information about the ticket. It demonstrates how to organize flat payload data into a more hierarchical structure, enhancing readability and accessibility. Additionally, a direct field mapping for action_on_reject is shown, illustrating how simple fields and complex objects can coexist within a single mapper configuration.

ARRAY []
Description: The ARRAY function is utilized to construct an array, allowing for the aggregation of multiple data elements, including static values, dynamic content derived from the payload, and nested arrays.

Output Type: array

Parameters:

Children: A list of elements to be included in the array. Each element is defined using a BenderDefinition, enabling the inclusion of both static and dynamically evaluated content. (Type: BenderDefinition list)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example MW Data Mapping: Creating an Array
For demonstration purposes, let's create a mapper that generates an array based on the provided test case structure, adapted to the example payload:

MW Data Mapping:

JSON
YAML

{
  "example_array": [
    "sys_created_by.display_value",
    "'Fixed Value'",
    "state.value",
    [
      "impact.display_value"
    ]
  ]
}
Expected Result:

JSON

{
  "example_array": ["kmok", "Fixed Value", "7", ["4 - Localized"]]
}
In this example, the ARRAY functionality is implicitly utilized to create an array named example_array. This array includes:

The display_value of sys_created_by, dynamically pulled from the payload.
A hardcoded string "Fixed Value".
The value of state, showcasing that dynamic content based on payload data can be directly included.
A nested array containing the display_value of impact, demonstrating how arrays can be nested within one another for complex data structures.
This illustrates the versatility of the ARRAY function in combining static values, dynamically derived data, and nested arrays to construct complex data structures tailored to specific requirements.

FLATTEN
Description: The FLATTEN operator is designed to streamline nested structures by expanding any array-type elements into a parent list, while non-list elements are simply copied over. This is particularly useful for consolidating data from various nested sources into a single, uniform array.

Output Type: array

Parameters:

Items: Specifies the elements to be flattened. This can include arrays, which are expanded, and non-array elements, which are included as-is in the resulting array. (Type: BenderDefinition array)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example MW Data Mapping: Flattening Nested Arrays
To demonstrate the FLATTEN functionality, let's create a mapper based on the structure of the provided test case, adapted to the example payload:

MW Data Mapping:

JSON
YAML

{
  "flattened_array": {
    "FLATTEN()": [
      "sys_updated_on.display_value",
      ["number.display_value", "state.display_value"],
      "sys_created_by.display_value",
      "impact.display_value"
    ]
  }
}
Expected Result:

JSON

{
  "flattened_array": ["2015-03-10 04:00:07", "INC12345", "Closed", "kmok", "4 - Localized"]
}
In this example, the FLATTEN function is used to combine elements from various fields of the payload into a single array. It takes a mix of individual elements and arrays:

The display_value of sys_updated_on is included as an individual element.
An array containing the display_values of number and state is expanded into the parent list.
The display_value of sys_created_by and impact are added as individual elements.
This demonstrates how FLATTEN effectively merges nested arrays and standalone elements into a cohesive list, simplifying the structure for easier data manipulation and access.

MERGE
Description: The MERGE function combines multiple objects into a single object. If there are any key conflicts between the objects, the value from the object that appears later in the sequence takes precedence. This allows for the creation of composite objects from disparate sources, with a clear resolution strategy for overlapping keys.

Output Type: object

Parameters:

Items: A list of objects to be merged together. Each item is defined using a BenderDefinition, enabling the inclusion of both statically defined objects and dynamically generated ones. (Type: BenderDefinition)
Example Usage
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example MW Data Mapping: Merging Objects
To illustrate the MERGE functionality, let's create a mapper that combines several objects, some of which share common keys, based on the structure of the provided test case:

MW Data Mapping:

JSON
YAML

{
  "merged_info": {
    "MERGE()": [
      {
        "ticket_number": "number.display_value",
        "created_by": "sys_created_by.display_value"
      },
      {
        "ticket_number": "'Overridden Ticket Number'",
        "status": "state.display_value"
      },
      {
        "impact": "impact.display_value"
      }
    ]
  }
}
Expected Result:

JSON

{
  "merged_info": {
    "ticket_number": "Overridden Ticket Number",
    "created_by": "kmok",
    "status": "Closed",
    "impact": "4 - Localized"
  }
}
In this example, the MERGE function is used to combine three objects:

The first object contains the original ticket_number and created_by derived from the payload.
The second object also specifies a ticket_number, which overrides the value from the first object due to its later position in the list, and adds a new key status.
The third object introduces an additional key, impact.
This demonstrates how MERGE effectively consolidates multiple objects into a single composite object, with later values taking precedence in the case of key conflicts, allowing for dynamic object construction and key-value updates.

List Manipulation Operators
MAP
Description:Applies a specified transformation to each element within an array or each entry in an object. When processing an object, it converts the object into an array of entries, each containing key and value fields. The transformation is defined by a converter, which can utilize additional context about the current loop iteration.

Output Type: array

Iterator Object loop

With the loop object you can reference the index of the iterator. loop has two keys index0 and index1. Respectively, you can reference the index of the loop on a 0-base or 1-base using these arguments.

Parameters:

Items: The array or object to be transformed. If an object is provided, it is converted into an array of {key, value} objects for processing. (Type: BenderDefinition)
Converter: The transformation to apply to each element. The converter has access to the original payload plus any values defined in context. (Type: BenderDefinition)
Context: Optional. Defines keys for accessing loop-specific information, such as the current item's value, its index, and the total length of the array. (Type: LoopContextKeys)
Example Usage with Provided Payload
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example 1: Transforming an Array of Incident Attributes
MW Data Mapping:

JSON
YAML

{
  "incident_attributes": {
    "MAP()": {
      "items": ["number.value", "state.value", "impact.value"],
      "converter": "$CONCAT([item, \"'processed'\"], \" \")"
    }
  }
}
Expected Result:

JSON

{
  "incident_attributes": [
    "INC12345 processed",
    "7 processed",
    "4 processed"
  ]
}
This example demonstrates using MAP to append the string " processed" to each specified item from the payload, showcasing a simple transformation applied to a manually specified array of values.

Example 2: Transforming Object Entries into a List of Descriptions
Assuming we want to transform the display_value entries of our payload into a list that describes each field:

MW Data Mapping:

JSON
YAML

{
  "descriptions_list": {
    "MAP()": {
      "items": {
        "upon_reject": "upon_reject.display_value",
        "sys_updated_on": "sys_updated_on.display_value",
        "number": "number.display_value",
        "state": "state.display_value",
        "sys_created_by": "sys_created_by.display_value",
        "impact": "impact.display_value"
      },
      "converter": "$CONCAT([item, \"'description'\"], \" \")"
    }
  }
}
Expected Result:

JSON

{
  "descriptions_list": [
    "Cancel all future Tasks description",
    "2015-03-10 04:00:07 description",
    "INC12345 description",
    "Closed description",
    "kmok description",
    "4 - Localized description"
  ]
}
This mapping constructs an object from specified fields and then uses MAP to append " description" to each value, converting the object's values into a list.

SORT
Description: Organizes elements within an list or an object according to a specified key. For objects, it first converts the object into an array of its values. The key parameter defines how to derive a sort key from each element, which determines the sort order. Additionally, a desc parameter can specify whether the sorting should be in descending order.

Output Type: array

Parameters:

Items: The array or object to be sorted. If an object is provided, it is treated as an array of its values for sorting purposes. (Type: BenderDefinition)
Key: The transformation applied to each element to generate a sort key. This determines the order in which elements are sorted. (Type: BenderDefinition)
Desc: Specifies whether the sorting should be in descending order. (Type: BenderDefinition, typically a boolean)
Context: Optional. Defines keys for accessing loop-specific information during the sort operation. (Type: LoopContextKeys)
Example Usage with Provided Payload
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example 1: Sorting Display Values
Let's say we want to sort the display_value fields of the payload's objects. First, we would need to transform the payload into a suitable array format that SORT can operate on.

MW Data Mapping:

JSON
YAML

{
  "sorted_display_values": {
    "SORT()": {
      "items": [
        "upon_reject.display_value",
        "sys_updated_on.display_value",
        "number.display_value",
        "state.display_value",
        "sys_created_by.display_value",
        "impact.display_value"
      ],
      "key": "item"
    }
  }
}
Expected Result:

JSON

{
  "sorted_display_values": [
    "2015-03-10 04:00:07",
    "4 - Localized",
    "Cancel all future Tasks",
    "Closed",
    "INC12345",
    "kmok"
  ]
}
This example aims to illustrate sorting a collection of the display_value fields from the payload.

Example 2: Sorting Object Values
Given a modified payload with object values:

JSON

{
  "values": {
    "ckey2": "cval",
    "ckey": "cval",
    "bkey2": "bval",
    "bkey": "bval",
    "akey2": "aval",
    "akey": "aval"
  }
}
MW Data Mapping:

JSON
YAML

{
  "sorted_object_values": {
    "SORT()": {
      "items": "values",
      "key": ["item", "loop.key"]
    }
  }
}
Expected Result:

JSON

{
  "sorted_object_values": ["aval", "aval", "bval", "bval", "cval", "cval"]
}
This example illustrates sorting the values of an object, converting the object into an array of its values, and then sorting those values in ascending order.

COALESCE
Description: Scans through the elements of items and returns the first element for which the condition evaluates to a truthy value. If the condition is not specified, it returns the first element that is inherently truthy according to standard truthiness evaluation in most programming languages.

Output Type: Varies based on the input items

Parameters:

Condition: An optional rule to determine the truthiness of each item. If omitted, a default truthiness evaluation is applied. (Type: BenderDefinition)
Items: The array or object to be evaluated. If an object is provided, it is converted into an array of its values. (Type: BenderDefinition)
Context: Optional. Provides additional keys for accessing specific information about each item during iteration. (Type: LoopContextKeys)
Given the provided example payload, let's demonstrate how the COALESCE operator can be applied in this context.

Example Usage with Provided Payload
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example: Finding the First Non-Empty display_value
MW Data Mapping:

JSON
YAML

{
  "first_non_empty_display_value": {
    "COALESCE()": {
      "items": [
        "upon_reject.display_value",
        "sys_updated_on.display_value",
        "number.display_value",
        "state.display_value",
        "sys_created_by.display_value",
        "impact.display_value"
      ],
      "condition": "item != ''"
    }
  }
}
Expected Result:

JSON

{
  "first_non_empty_display_value": "Cancel all future Tasks"
}
This example demonstrates using COALESCE to find the first non-empty display_value across various fields in the payload. Given all display_value fields are non-empty, it returns the first one, "Cancel all future Tasks".

Example 2: Coalesce Without Condition (Hit)
Given a payload where we are looking for the first truthy value in an array:

JSON

{
  "values": [0, "", null, false, {}, [], 12]
}
MW Data Mapping:

JSON
YAML

{
  "first_truthy_value": {
    "COALESCE()": {
      "items": "values"
    }
  }
}
Expected Result:

JSON

{
  "first_truthy_value": 12
}
In this example, COALESCE scans through the list values and returns the first truthy value it encounters, which is 12. This is because all other values (0, '', null, false, {}, []) are considered falsy in most programming contexts, leaving 12 as the first truthy value.

Example 3: Coalesce Without Condition (Miss)
Given a payload where no elements meet the truthiness criteria:

JSON

{
  "values": [0, "", null, false, {}, []]
}
MW Data Mapping:

JSON
YAML

{
  "first_truthy_value": {
    "COALESCE()": {
      "items": "values"
    }
  }
}
Expected Result:

JSON

{
  "first_truthy_value": null
}
In this scenario, since none of the elements in the list values are truthy, COALESCE returns null, indicating that no suitable element was found.

Example 4: Coalesce With Condition (Hit)
Given a payload and a condition to find the first item greater than 4:

JSON

{
  "values": [0, 2, 4, 6, "fail - tests early exit"]
}
MW Data Mapping:

JSON
YAML

{
  "first_item_greater_than_four": {
    "COALESCE()": {
      "items": "values",
      "condition": "item > 4"
    }
  }
}
Expected Result:

JSON

{
  "first_item_greater_than_four": 6
}
This example demonstrates using COALESCE with a condition (item > 4). It evaluates each element against the condition and returns the first one that satisfies it, which is 6. Note that the string "fail - tests early exit" is ignored in the condition evaluation because it does not meet the numerical comparison.

FILTER
Description: Evaluates each element within items against a specified condition, returning a listlist of all elements for which the condition evaluates to a truthy value. If the condition is omitted, FILTER defaults to using a truthiness filter, returning all inherently truthy elements.

Output Type: list

Parameters:

Condition: An optional rule for evaluating the truthiness of each item. If omitted, a default truthiness evaluation is applied. (Type: BenderDefinition)
Items: The array or object to be filtered. If an object is provided, it is considered as an array of its values. (Type: BenderDefinition)
Context: Optional. Provides additional keys for accessing specific information about each item during iteration. (Type: LoopContextKeys)
Examples Based on Test Cases
Example 1: Filter Without Condition
Given a payload:

JSON

{
  "values": [0, 1, "", "a", false, true, [], ["a"], {}, {"a": "b"}, null]
}
MW Data Mapping:

JSON
YAML

{
  "filtered_values": {
    "FILTER()": {
      "items": "values"
    }
  }
}
Expected Result:

JSON

{
  "filtered_values": [1, "a", true, ["a"], {"a": "b"}]
}
This example demonstrates the default behavior of FILTER when no condition is specified. It returns all truthy values from the values array, effectively filtering out 0, "", false, [], {}, and null.

Example 2: Filter With Condition
Given a payload:

JSON

{
  "values": [0, 1, 2, 3, 4, 5, 6]
}
MW Data Mapping:

JSON
YAML

{
  "filtered_values": {
    "FILTER()": {
      "items": "values",
      "condition": "item > 3"
    }
  }
}
Expected Result:

JSON

{
  "filtered_values": [4, 5, 6]
}
In this scenario, FILTER is applied with a condition (item > 3), returning an array of values that are greater than 3.

Additional Example: Filtering Objects
Given a payload that is not directly related to the test cases but demonstrates filtering with objects:

JSON

{
  "people": {
    "john": {"age": 28},
    "jane": {"age": 34},
    "doe": {"age": 17}
  }
}
MW Data Mapping:

JSON
YAML

{
  "adults": {
    "FILTER()": {
      "items": "people",
      "condition": "item.age >= 18"
    }
  }
}
Expected Result:

JSON

{
  "adults": [{"age": 28}, {"age": 34}]
}
This additional example showcases how FILTER can be applied to an object, considering it as an array of its values, and using a condition to filter based on a specific property (age in this case). Note that the original keys (john, jane) are not preserved in the output, as the object is treated as an array of values for filtering purposes.

Branching Operators
CONDITIONAL
Description: The CONDITIONAL operator evaluates a given condition and returns the result of on_pass if the condition is truthy, or on_fail if the condition is falsy. This operator allows for branching logic within the data transformation process, making it versatile for conditional data handling.

Parameters:

Condition: The condition to evaluate for truthiness.
On_pass: The operation or value to return if the condition is truthy.
On_fail: The operation or value to return if the condition is falsy.
Context: Optional. A set of precalculated arguments to use during evaluation, allowing for more complex conditions or return values.
Example 1: Conditional Pass Without Context
Given a payload:

JSON

{
  "val": true,
  "text": "success"
}
MW Data Mapping:

JSON
YAML

{
  "result": {
    "CONDITIONAL()": {
      "condition": "val",
      "on_pass": "text"
    }
  }
}
Expected Result:

JSON

{
  "result": "success"
}
This example demonstrates a basic conditional check where the val is true, leading to the on_pass value being returned.

Example 2: Conditional Fail Without Context
Given a payload:

JSON

{
  "val": false,
  "text": "failure"
}
MW Data Mapping:

JSON
YAML

{
  "result": {
    "CONDITIONAL()": {
      "condition": "val",
      "on_fail": "text"
    }
  }
}
Expected Result:

JSON

{
  "result": "failure"
}
This example demonstrates the on_fail path being taken when the condition evaluates to false.

Example 3: Conditional using relationship operators
Let's apply a conditional operation to the provided example payload, using the state value to determine an action:

Given the example payload:

JSON

{
  "state": {
    "display_value": "Closed",
    "value": "7"
  }
}
MW Data Mapping:

JSON
YAML

{
  "action_required": {
    "CONDITIONAL()": {
      "condition": "state.value == '7'",
      "on_pass": "'No further action required'",
      "on_fail": "'Action required'"
    }
  }
}
Expected Result:

JSON

{
  "action_required": "No further action required"
}
In this scenario, we're checking if the state value is '7', which corresponds to a "Closed" state. Since the condition is met, the on_pass value is returned, indicating that no further action is required.

LOOKUP
Description: The LOOKUP operator searches for a specified key within a provided mapping and returns the corresponding output. If the key is not found, an optional default value can be returned instead.

Parameters:

Key: The key to search for within the mapping.
Mapping: A dictionary or map where each key is associated with a transformation rule or value.
Default: Optional. The value to return if the key is not found in the mapping.
Example 1: Lookup Hit and Map
Given a payload:

JSON

{
  "i": "a",
  "value1": "success"
}
MW Data Mapping:

JSON
YAML

{
  "result": {
    "LOOKUP()": {
      "key": "i",
      "mapping": {
        "a": "value1",
        "b": "'value2'",
        "c": {
          "key": "value3"
        }
      }
    }
  }
}
Expected Result:

JSON

{
  "result": "success"
}
This example demonstrates a lookup operation where the key i has the value "a", leading to the lookup of "a" in the mapping and returning the corresponding value associated with "value1" in the payload.

Example 2: Lookup Hit and Constant
Given a payload:

JSON

{
  "i": "b"
}
MW Data Mapping (Same as Example 1):

Expected Result:

JSON

{
  "result": "value2"
}
In this scenario, the key i with value "b" matches directly to a constant "value2" defined in the mapping.

Given the Payload
JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example 3: Lookup Hit
MW Data Mapping:

JSON
YAML

{
  "state_description": {
    "LOOKUP()": {
      "key": "state.value",
      "mapping": {
        "1": "'New'",
        "2": "'In Progress'",
        "3": "'On Hold'",
        "7": "'Closed'"
      },
      "default": "'Unknown State'"
    }
  }
}
Expected Result:

JSON

{
  "state_description": "Closed"
}
In this example, the LOOKUP operation uses the state.value ("7") as the key to find a matching entry in the provided mapping. Since there is a match, it returns the corresponding descriptive status, "Closed".

Example 4: Lookup Miss with Default
Let's assume we're looking up the impact based on its value to provide a more detailed explanation, but the impact value is not in our mapping.

MW Data Mapping:

JSON
YAML

{
  "impact_description": {
    "LOOKUP()": {
      "key": "impact.value",
      "mapping": {
        "1": "'High'",
        "2": "'Medium'",
        "3": "'Low'"
      },
      "default": "'Impact not specified'"
    }
  }
}
Expected Result:

JSON

{
  "impact_description": "Impact not specified"
}
For this scenario, since the impact.value is "4" and does not match any keys in the mapping, the LOOKUP operation returns the default value, "Impact not specified".

String Manipulation Operators
CONCAT
Description: Combines a list of strings into a final composite string, with an optional separator inserted between elements.

Parameters:

Separator: A string value to insert between elements.
Items: Elements to be combined into a single composite string.
Example Usage with Provided Payload
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example: Concatenating display_value Fields with Separator
Let's concatenate the display_value fields of various properties in the payload, using a specific separator.

MW Data Mapping:

JSON
YAML

{
  "concatenated_display_values": {
    "CONCAT()": {
      "items": [
        "upon_reject.display_value",
        "sys_updated_on.display_value",
        "number.display_value",
        "state.display_value",
        "sys_created_by.display_value",
        "impact.display_value"
      ],
      "separator": " | "
    }
  }
}
Expected Result:

JSON

{
  "concatenated_display_values": "Cancel all future Tasks | 2015-03-10 04:00:07 | INC12345 | Closed | kmok | 4 - Localized"
}
This example demonstrates using CONCAT to join the display_value fields of various properties with a separator " | ", creating a single, readable string that combines all the specified values.

RENDER
Description: The RENDER operator utilizes a Mustache template to generate a string output based on provided args. If args are omitted, the root object is used by default.

Parameters:

Template: A Mustache template string.
Args: Optional. Pre-calculated arguments to be used within the template.
If you are accessing an array index, you will need to access it with dot notation . instead bracket notation []. For example, if want to access the first element of a given array called first_list, you would need to access the array element as first_list.0 since the Render function does not support bracket notation.

Example Usage with Provided Payload
Given the example payload:

JSON

{
  "upon_reject": {
    "display_value": "Cancel all future Tasks",
    "value": "cancel"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  },
  "state": {
    "display_value": "Closed",
    "value": "7"
  },
  "sys_created_by": {
    "display_value": "kmok",
    "value": "kmok"
  },
  "impact": {
    "display_value": "4 - Localized",
    "value": "4"
  }
}
Example: RENDER with No Args
MW Data Mapping:

JSON
YAML

{
  "summary": {
    "RENDER()": {
      "template": "Incident {{ number.display_value }} was created by {{ sys_created_by.display_value }} on {{ sys_updated_on.display_value }}. Its current state is {{ state.display_value }}."
    }
  }
}
Expected Result:

JSON

{
  "summary": "Incident INC12345 was created by kmok on 2015-03-10 04:00:07. Its current state is Closed."
}
This example demonstrates using RENDER with a Mustache template to generate a summary string directly from the root object (payload), as no args are specified.

Example: RENDER with Args
MW Data Mapping:

JSON

custom_summary:
  RENDER():
    template: >-
      The incident with number {{ incident_number }} has {{ impact_description
      }}.
    args:
      incident_number: number.display_value
      impact_description:
        LOOKUP():
          key: impact.value
          mapping:
            '1': "'Critical impact'"
            '2': "'Major impact'"
            '3': "'Minor impact'"
            '4': "'Localized impact'"
          default: "'an unspecified impact'"
Expected Result:

JSON

{
  "custom_summary": "The incident with number INC12345 has Localized impact."
}
In this example, RENDER is used with a Mustache template and custom args to generate a more detailed summary. The args include direct references to payload values and a LOOKUP operation to provide a more descriptive impact level.

STRIP_HTML
Description: The STRIP_HTML operator processes a given HTML string (text), stripping away HTML tags and returning the plain text content.

Parameters:

Text: The raw HTML text to be converted to plain text.
Example Usage with a Payload that contains an html display value
Let's assume we have a payload where one of the fields contains HTML content, similar to the structure of the provided payloads:

JSON

{
  "description": {
    "display_value": "<div>Issue reported: <strong>System crash</strong> on <em>2023-03-10</em>.</div><div>Urgency: <span style='color:red;'>High</span></div>",
    "value": "description_value"
  },
  "sys_updated_on": {
    "display_value": "2015-03-10 04:00:07",
    "value": "2015-03-10 04:00:07"
  },
  "number": {
    "display_value": "INC12345",
    "value": "INC12345"
  }
}
Example: Stripping HTML from a Description Field
MW Data Mapping:

JSON
YAML

{
  "plain_text_description": {
    "STRIP_HTML()": "description.display_value"
  }
}
Expected Result:

JSON

{
  "plain_text_description": "Issue reported: System crash on 2023-03-10.\nUrgency: High"
}
This example demonstrates the use of STRIP_HTML to convert an HTML-formatted description into plain text, improving readability and ensuring the content is suitable for contexts where HTML rendering is not available or desired.