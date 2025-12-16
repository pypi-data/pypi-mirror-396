print("Package mypyy Loaded. Run py.help() for list of practicals.")

def basic_io():
    print(r'''
# Practical 1: Basic Input, Output, and Variables

# Input
name = input("Enter your name: ")

# Variable (stores value)
age = 20

# Output
print("Hello,", name)
print("Your age is:", age)

# Identifier example
student_name = "Anand"
print("Identifier example:", student_name)
''')


def arithmetic_ops():
    print(r'''
# Practical 2: Arithmetic Operators

a = 10
b = 3

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor Division:", a // b)
print("Modulus:", a % b)
print("Exponent:", a ** b)
''')


def control_structures():
    print(r'''
# Practical 3: Control Structures (Loops & Conditions)

# If-Else
x = 5
if x > 0:
    print("Positive")
else:
    print("Negative")

# Loop For
for i in range(1, 6):
    print("For Loop:", i)

# While Loop
count = 1
while count <= 5:
    print("While Loop:", count)
    count += 1
''')


def basic_functions():
    print(r'''
# Practical 4: Basic Functions

def greet():
    print("Hello from function")

greet()

# Function with parameters
def add(a, b):
    return a + b

print("Addition using function:", add(5, 7))
''')


def recursion_factorial():
    print(r'''
# Practical 5: Recursion (Factorial)

def fact(n):
    if n == 1:
        return 1
    else:
        return n * fact(n - 1)

print("Factorial of 5:", fact(5))
''')


def recursion_user_input():
    print(r'''
# Practical 6: Recursion with User Input

def fact(n):
    if n == 1:
        return 1
    else:
        return n * fact(n - 1)

# Taking input from user
num = int(input("Enter a number to find factorial: "))
print("Factorial of", num, "is:", fact(num))
''')


def list_ops():
    print(r'''
# Practical 7: List Operations

numbers = [10, 20, 30]

# 1. Append - adds element at end
numbers.append(40)
print("After append:", numbers)

# 2. Extend - add multiple elements
numbers.extend([50, 60])
print("After extend:", numbers)

# 3. Insert - insert at specific position
numbers.insert(1, 15)
print("After insert:", numbers)

# 4. Remove - removes specific item
numbers.remove(30)
print("After remove:", numbers)

# 5. Pop - removes last element / index element
numbers.pop() # last element
numbers.pop(2) # index 2
print("After pop:", numbers)

# 6. Slice - extracts part of list
print("Sliced list (0 to 3):", numbers[0:3])
''')


def set_ops():
    print(r'''
# Practical 8: Set Operations

s = {10, 20, 30}

# 1. Update - add multiple values
s.update([40, 50])
print("After update:", s)

# 2. Remove element
s.remove(20)
print("After remove:", s)

# 3. Clear - removes all elements
temp = s.copy() # to show before and after
temp.clear()
print("After clear:", temp)

# 4. Pop - removes random element
s.pop()
print("After pop:", s)
''')


def tuple_ops():
    print(r'''
# Practical 9: Tuple Operations

t = (10, 20, 30, 40, 50)

# 1. Accessing
print("Access index 2:", t[2])

# 2. Concatenation
t2 = (60, 70)
t3 = t + t2
print("Concatenated tuple:", t3)

# 3. Slicing
print("Tuple slice (1 to 4):", t[1:4])

# 4. Deleting (tuple cannot delete element; but whole tuple can be deleted)
# del t
print("Tuple deleted successfully (simulated)")
''')


def dict_ops():
    print(r'''
# Practical 10: Dictionary Operations

student = {"name": "Anand", "age": 20, "city": "Pune"}

# Access value
print("Name:", student["name"])

# Add new key-value
student["course"] = "Computer Science"
print("After adding:", student)

# Update value
student["age"] = 21
print("After updating age:", student)

# Remove element
student.pop("city")
print("After pop:", student)
''')


def string_methods():
    print(r'''
# Practical 11: Basic String Methods

text = "Hello Python"

# Length
print("Length:", len(text))

# Slice
print("Slice (0 to 5):", text[0:5])

# Uppercase
print("Upper:", text.upper())

# Lowercase
print("Lower:", text.lower())

# Replace
print("Replace Python:", text.replace("Python", "World"))

# Concatenation
result = text + " Programming"
print("Concatenation:", result)
''')


def string_manipulation():
    print(r'''
# Practical 12: Interactive String Manipulation

# Taking input from user
text = input("Enter a string: ")

# 1. Slicing
print("\n--- Slicing ---")
print("First 5 characters:", text[0:5])
print("Characters from index 2 to 8:", text[2:8])
print("Last 3 characters:", text[-3:])

# 2. Concatenation
print("\n--- Concatenation ---")
extra = input("Enter another string to concatenate: ")
print("Concatenated string:", text + " " + extra)

# 3. Finding the length of the string
print("\n--- Length of String ---")
print("Length of the string:", len(text))

# 4. Uppercase and Lowercase
print("\n--- Uppercase & Lowercase ---")
print("Uppercase:", text.upper())
print("Lowercase:", text.lower())

# 5. Replacing a substring with another substring
print("\n--- Replace Substring ---")
old = input("Enter substring to replace: ")
new = input("Enter new substring: ")
print("Updated string:", text.replace(old, new))

# 6. Splitting string into list of substrings
print("\n--- Split String ---")
print("Split by space:", text.split())
print("Split by comma (if any):", text.split(','))
''')


def file_handling():
    print(r'''
# Practical 13: File Handling Operations
import os

filename = "sample.txt"

# 1. CREATE a new file and WRITE default text
print("\n--- Creating File ---")
with open(filename, "w") as f:
    f.write("Hello! This is the first line in the file.\n")
print("File created and initial text written.")

# 2. OPEN and READ the file
print("\n--- Reading File ---")
with open(filename, "r") as f:
    data = f.read()
print("File contents:\n", data)

# 3. WRITE/OVERWRITE file (clears old data)
print("\n--- Writing (Overwrite) File ---")
with open(filename, "w") as f:
    f.write("This text overwrites the previous content.\n")
print("File overwritten successfully.")

# 4. UPDATE / APPEND data to the file
print("\n--- Updating (Appending) File ---")
with open(filename, "a") as f:
    f.write("This is an appended line.\n")
    f.write("Appending more text!\n")
print("Data appended successfully.")

# Read again after update
print("\n--- Reading After Update ---")
with open(filename, "r") as f:
    print(f.read())

# 5. DELETE the file
print("\n--- Deleting File ---")
if os.path.exists(filename):
    os.remove(filename)
    print(f"{filename} deleted successfully.")
else:
    print("File does not exist.")
''')


def all():
    print("="*50)
    print(" PRINTING ALL PRACTICAL CODES ")
    print("="*50)
    print("\n--- BASIC_IO ---\n")
    basic_io()
    print("-" * 50)
    print("\n--- ARITHMETIC_OPS ---\n")
    arithmetic_ops()
    print("-" * 50)
    print("\n--- CONTROL_STRUCTURES ---\n")
    control_structures()
    print("-" * 50)
    print("\n--- BASIC_FUNCTIONS ---\n")
    basic_functions()
    print("-" * 50)
    print("\n--- RECURSION_FACTORIAL ---\n")
    recursion_factorial()
    print("-" * 50)
    print("\n--- RECURSION_USER_INPUT ---\n")
    recursion_user_input()
    print("-" * 50)
    print("\n--- LIST_OPS ---\n")
    list_ops()
    print("-" * 50)
    print("\n--- SET_OPS ---\n")
    set_ops()
    print("-" * 50)
    print("\n--- TUPLE_OPS ---\n")
    tuple_ops()
    print("-" * 50)
    print("\n--- DICT_OPS ---\n")
    dict_ops()
    print("-" * 50)
    print("\n--- STRING_METHODS ---\n")
    string_methods()
    print("-" * 50)
    print("\n--- STRING_MANIPULATION ---\n")
    string_manipulation()
    print("-" * 50)
    print("\n--- FILE_HANDLING ---\n")
    file_handling()
    print("-" * 50)


def help():
    print("\nAvailable Commands:")
    print("-------------------")
    methods = [
        'basic_io',
        'arithmetic_ops',
        'control_structures',
        'basic_functions',
        'recursion_factorial',
        'recursion_user_input',
        'list_ops',
        'set_ops',
        'tuple_ops',
        'dict_ops',
        'string_methods',
        'string_manipulation',
        'file_handling',
    ]
    for m in methods:
        print(f"py.{m}()")
    print("\nSpecial:")
    print("py.all()")
    print("py.help()")
