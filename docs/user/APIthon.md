How APIthon Works
The most important thing to remember about APIthon is that it returns the result from the last line of code

Let's look at some examples:

Python

cookies = 5
more_cookies = 3
cookies + more_cookies
This will give us back 8, because adding cookies is the last thing we did! But if we write:

Python

cookies = 5
cookies + 3
more_cookies = 2
We won't get anything back, because the last thing we did was just make a new variable!

Python vs. APIthon
Capabilities
No Imports
You cannot import any external modules or packages
You can only use the built-in functions that are available
No Classes
You cannot define new classes
You must work with existing data types
No Private Methods or Properties
Anything that starts with an underscore (_) is off-limits
This includes both methods and variables
No External Code
All code must be self-contained
No accessing external resources
No Multiple Language Support
APIthon only works with Python-style syntax
No mixing with other programming languages
Size Limits
APIthon also has some size limits:

Your code can't be too long (4096 bytes)
Your lists can't have too many things in them (2096 bytes)
Your numbers can't be too big or too small (4294967296)
Your words (strings) can't be too long (4096 bytes/characters)
Using APIthon
Common Operations
APIthon supports many common operations across different data types. Here are the most useful ones you'll likely use:

Working with Numbers (Integers and Floats)
Python

# Basic math operations
number = 5
other = 3
number + other # Addition
number - other # Subtraction
number * other # Multiplication
number / other # Division
number // other # Floor division
number % other # Modulus (remainder)
number ** other # Power# Comparison
number > other # Greater than
number < other # Less than
number >= other # Greater than or equal
number <= other # Less than or equal
number == other # Equal to

Working with Text (Strings)
Python

text = "Hello"
other = "World"

# String operations
text + other # Joining strings
text * 3 # Repeat string
text.split() # Split into list
text.join(['a','b']) # Join list into string
text.replace('l', 'w') # Replace characters

Working with Lists
Python

my_list = [1, 2, 3]

# List operations
my_list.append(4) # Add item to end
my_list.pop() # Remove and return last item
my_list.remove(2) # Remove specific item
my_list.index(1) # Find position of item
my_list.sort() # Sort the list
my_list.reverse() # Reverse the list
len(my_list) # Get length of list

Working with Sets
Python

set_a = {1, 2, 3}
set_b = {3, 4, 5}

# Set operations
set_a.add(4) # Add item
set_a.remove(2) # Remove item
set_a & set_b # Intersection
set_a | set_b # Union
set_a - set_b # Difference

Working with Dictionaries
Python

my_dict = {"name": "Alice"}

# Dictionary operations
my_dict["age"] = 20 # Add/update item
my_dict.get("name") # Get value safely
my_dict.keys() # Get all keys
my_dict.values() # Get all values

Common Built-in Functions
Python

len(something) # Get length
str(42) # Convert to string
int("42") # Convert to integer
float("42.5") # Convert to float
bool(1) # Convert to boolean

Remember these important points about functions in APIthon:

All functions return values (just like in a Python shell)
The last operation's result is what gets returned
There are limits on how many operations you can perform
If a function name starts with underscore (_), you can't use it
APIthon Examples
Example 1: Joining a list of strings
YAML

script:
  output_key: uppercase_names
  input_args:
    names: data.user_list.names
  code: "','.join(names)"
This takes a list of names and join them together into a single string!

Sample Input Payload:

Python

data.user_list.names = ["Alice", "Bob", "Charlie"]
Result:

Python

Alice,Bob,Charlie
Example 2: Calculating Total Points
YAML

script:
  output_key: total_score
  input_args:
    scores: data.game_results.points
  code: "total = 0; [total := total + score for score in scores if score > 0]; total"
This adds up all the positive scores in a list!

Sample Input Payload:

Python

data.game_results.points = [10, -5, 20, 0, 15]
Result:

Python

45
Example 3: Organizing a Pet Directory
YAML

script:
  output_key: pet_summary
  input_args:
    pets: data.pet_store.animals
  code: |
    pet_types = {}

    for pet in pets:
        pet_type = pet.get('type')
        if pet_type not in pet_types:
            pet_types[pet_type] = []
        pet_types[pet_type].append(pet.get('name'))

    summary = ""
    for pet_type in pet_types:
        names = pet_types[pet_type]
        summary += f"We have {len(names)} {pet_type}(s):\n"
        for name in names:
            summary += f"- {name}\n"
        summary += "\n"

    summary
This organizes a list of pets by type and creates a nice summary!

Sample Input Payload:

Python

data.pet_store.animals = [
    {"type": "dog", "name": "Buddy"},
    {"type": "cat", "name": "Whiskers"},
    {"type": "dog", "name": "Max"},
    {"type": "fish", "name": "Nemo"}
]
Result:


We have 2 dog(s):
- Buddy
- Max

We have 1 cat(s):
- Whiskers

We have 1 fish(s):
- Nemo
Example 4: Grade Calculator
YAML

script:
  output_key: grade_report
  input_args:
    grades: data.student_records.scores
  code: |
    def calculate_grade(score):
        if score >= 90: return 'A'
        if score >= 80: return 'B'
        if score >= 70: return 'C'
        if score >= 60: return 'D'
        return 'F'

    total = 0
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

    for score in grades:
        total += score
        grade = calculate_grade(score)
        grade_counts[grade] += 1

    average = total / len(grades)

    report = f"Class Average: {average:.2f}\n\nGrade Distribution:\n"
    for grade, count in grade_counts.items():
        report += f"Grade {grade}: {count} students\n"

    report
This takes a list of grades, calculates statistics, and creates a detailed report!

Sample Input Payload:

Python


data.student_records.scores = [95, 82, 74, 65, 88, 90, 55, 89, 92, 78]
Result:


Class Average: 80.80

Grade Distribution:
Grade A: 3 students
Grade B: 4 students
Grade C: 1 students
Grade D: 1 students
Grade F: 1 students

Troubleshooting
Remember to use | after code: to tell the editor that you're about to write multiline code
Make sure your indentation is correct - Python is very picky about this!
The last line of your code is what gets saved to your output_key
Be aware of the size limits when working with collections