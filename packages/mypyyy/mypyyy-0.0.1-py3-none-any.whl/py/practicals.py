import inspect
import os

def display_source(func):
    """Decorator to print source code before execution."""
    def wrapper(*args, **kwargs):
        print(f"\n{'='*20} Source Code: {func.__name__} {'='*20}")
        try:
            source = inspect.getsource(func)
            print(source)
        except OSError:
            print("# Source code not available (interactive shell or compiled).")
        print(f"{'='*25} Execution {'='*25}\n")
        return func(*args, **kwargs)
    return wrapper

@display_source
def io():
    """Basic Input, Output, and Variables (Prac 1)"""
    # Input
    print("--- Input ---")
    name = input("Enter your name: ")
    
    # Variable (stores value)
    age = 20
    
    # Output
    print("\n--- Output ---")
    print("Hello,", name)
    print("Your age is:", age)
    
    # Identifier example
    student_name = "Anand"
    print("Identifier example:", student_name)

@display_source
def calc():
    """Arithmetic Operators (Prac 2)"""
    a = 10
    b = 3
    print(f"a = {a}, b = {b}")
    print("Addition (a + b):", a + b)
    print("Subtraction (a - b):", a - b)
    print("Multiplication (a * b):", a * b)
    print("Division (a / b):", a / b)
    print("Floor Division (a // b):", a // b)
    print("Modulus (a % b):", a % b)
    print("Exponent (a ** b):", a ** b)

@display_source
def loops():
    """Control Structures - Loops/If-Else (Prac 3)"""
    # If-Else
    print("--- If-Else ---")
    x = 5
    if x > 0:
        print(f"x is {x}: Positive")
    else:
        print(f"x is {x}: Negative")

    # Loop For
    print("\n--- For Loop ---")
    for i in range(1, 6):
        print("For Loop:", i)

    # While Loop
    print("\n--- While Loop ---")
    count = 1
    while count <= 5:
        print("While Loop:", count)
        count += 1

@display_source
def funcs():
    """Basic Functions (Prac 4)"""
    print("--- Defining and Calling Functions ---")
    
    def greet():
        print("Hello from function")

    greet()

    # Function with parameters
    def add(a, b):
        return a + b

    result = add(5, 7)
    print(f"Addition using function add(5, 7): {result}")

@display_source
def fact():
    """Recursion - Factorial (Prac 5)"""
    print("--- Recursive Factorial ---")
    
    def fact_recursion(n):
        if n == 1:
            return 1
        else:
            return n * fact_recursion(n - 1)
            
    print("Factorial of 5:", fact_recursion(5))

@display_source
def fact_input():
    """Recursion with User Input (Prac 6)"""
    print("--- Recursive Factorial (User Input) ---")
    
    def fact_recursion(n):
        if n <= 1:
            return 1
        else:
            return n * fact_recursion(n - 1)
    
    try:
        num_str = input("Enter a number to find factorial: ")
        num = int(num_str)
        print("Factorial of", num, "is:", fact_recursion(num))
    except ValueError:
        print("Please enter a valid integer.")

@display_source
def lists():
    """List Operations (Prac 7)"""
    print("--- List Operations ---")
    numbers = [10, 20, 30]
    print("Original:", numbers)

    # 1. Append
    numbers.append(40)
    print("After append(40):", numbers)

    # 2. Extend
    numbers.extend([50, 60])
    print("After extend([50, 60]):", numbers)

    # 3. Insert
    numbers.insert(1, 15)
    print("After insert(1, 15):", numbers)

    # 4. Remove
    numbers.remove(30)
    print("After remove(30):", numbers)

    # 5. Pop
    numbers.pop() # last element
    print("After pop() (last):", numbers)
    numbers.pop(2) # index 2
    print("After pop(2):", numbers)

    # 6. Slice
    print("Sliced list (0 to 3):", numbers[0:3])

@display_source
def sets():
    """Set Operations (Prac 8)"""
    print("--- Set Operations ---")
    s = {10, 20, 30}
    print("Original Set:", s)

    # 1. Update
    s.update([40, 50])
    print("After update([40, 50]):", s)

    # 2. Remove
    if 20 in s:
        s.remove(20)
        print("After remove(20):", s)

    # 3. Pop
    popped = s.pop()
    print(f"After pop() [removed {popped}]:", s)
    
    # 4. Clear
    temp = s.copy()
    temp.clear()
    print("After clear (on copy):", temp)

@display_source
def tuples():
    """Tuple Operations (Prac 9)"""
    print("--- Tuple Operations ---")
    t = (10, 20, 30, 40, 50)
    print("Original Tuple:", t)

    # 1. Accessing
    print("Access index 2:", t[2])

    # 2. Concatenation
    t2 = (60, 70)
    t3 = t + t2
    print(f"Concatenated with {t2}:", t3)

    # 3. Slicing
    print("Tuple slice (1 to 4):", t[1:4])

    # 4. Deleting
    # Note: We cannot delete elements, but we can delete the variable
    print("Deleting tuple object...")
    del t
    try:
        print(t)
    except UnboundLocalError:
        print("Tuple deleted successfully (variable no longer exists).")

@display_source
def dicts():
    """Dictionary Operations (Prac 10)"""
    print("--- Dictionary Operations ---")
    student = {"name": "Anand", "age": 20, "city": "Pune"}
    print("Original:", student)

    # Access value
    print("Name:", student["name"])

    # Add new key-value
    student["course"] = "Computer Science"
    print("After adding course:", student)

    # Update value
    student["age"] = 21
    print("After updating age:", student)

    # Remove element
    if "city" in student:
        student.pop("city")
    print("After pop('city'):", student)

@display_source
def str_basic():
    """Basic String Methods (Prac 11)"""
    print("--- String Operations ---")
    text = "Hello Python"
    print(f"Text: '{text}'")

    # Length
    print("Length:", len(text))

    # Slice
    print("Slice (0 to 5):", text[0:5])

    # Uppercase
    print("Upper:", text.upper())

    # Lowercase
    print("Lower:", text.lower())

    # Replace
    print("Replace 'Python' with 'World':", text.replace("Python", "World"))

    # Concatenation
    result = text + " Programming"
    print("Concatenation:", result)

@display_source
def str_inter():
    """Interactive String Manipulation (Prac 12)"""
    print("--- Interactive String Ops ---")
    text = input("Enter a string: ")

    # 1. Slicing
    print("\n--- Slicing ---")
    print("First 5 characters:", text[0:5])
    if len(text) > 8:
        print("Characters from index 2 to 8:", text[2:8])
    print("Last 3 characters:", text[-3:])

    # 2. Concatenation
    print("\n--- Concatenation ---")
    extra = input("Enter another string to concatenate: ")
    print("Concatenated string:", text + " " + extra)

    # 3. Length
    print("\n--- Length of String ---")
    print("Length of the string:", len(text))

    # 4. Upper/Lower
    print("\n--- Uppercase & Lowercase ---")
    print("Uppercase:", text.upper())
    print("Lowercase:", text.lower())

    # 5. Replace
    print("\n--- Replace Substring ---")
    old = input("Enter substring to replace: ")
    new = input("Enter new substring: ")
    print("Updated string:", text.replace(old, new))

    # 6. Split
    print("\n--- Split String ---")
    print("Split by space:", text.split())
    print("Split by comma:", text.split(','))

@display_source
def files():
    """File Handling Operations (Prac 13)"""
    print("--- File Handling ---")
    filename = "sample.txt"

    # 1. CREATE and WRITE
    print("\n1. Creating File...")
    with open(filename, "w") as f:
        f.write("Hello! This is the first line in the file.\n")
    print("File created and initial text written.")

    # 2. OPEN and READ
    print("\n2. Reading File...")
    with open(filename, "r") as f:
        data = f.read()
    print(f"File contents:\n{data}")

    # 3. OVERWRITE
    print("\n3. Writing (Overwrite) File...")
    with open(filename, "w") as f:
        f.write("This text overwrites the previous content.\n")
    print("File overwritten successfully.")

    # 4. APPEND
    print("\n4. Updating (Appending) File...")
    with open(filename, "a") as f:
        f.write("This is an appended line.\n")
        f.write("Appending more text!\n")
    print("Data appended successfully.")

    # Read again
    print("\n--- Reading After Update ---")
    with open(filename, "r") as f:
        print(f.read())

    # 5. DELETE
    print("\n5. Deleting File...")
    if os.path.exists(filename):
        os.remove(filename)
        print(f"{filename} deleted successfully.")
    else:
        print("File does not exist.")
