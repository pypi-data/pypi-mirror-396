# -------------DSA-------------

insert_element = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, pos, value;

    cout << "Size of Array: ";
    cin >> size;

    cout << "Enter the elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the element to insert: ";
    cin >> value;
    cout << "Enter the position to insert: ";
    cin >> pos;

    if (pos<0 || pos>size){
        cout << "Invalid position!" << endl;
    }
    else {
        for (int i = size; i > pos; i--){
            arr[i] = arr[i - 1];
        }

        arr[pos] = value;
        size++;
        cout << "Array after insertion: " << endl;
        for (int i = 0; i < size; i++) {
            cout << arr[i] << " ";
        }
    }

    return 0;
}
"""

delete_element = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, pos;

    cout << "Size of Array: ";
    cin >> size;

    cout << "Enter the elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the position: ";
    cin >> pos;

    if (pos <0 || pos >=size) {
        cout << "Invalid position!" << endl;
    } else {
        for (int i = pos; i < size - 1; i++) {
            arr[i] = arr[i + 1];
        }

        size--;
        cout << "Array after deletion: " << endl;
        for (int i = 0; i < size; i++) {
            cout << arr[i] << " ";
        }
        cout << endl;
    }
    return 0;
}
"""
linear_search = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, value;
    int loc = -1; 

    cout << "Enter the size of array: ";
    cin >> size;

    cout << "Enter elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter the element to find: ";
    cin >> value;

    for (int i = 0; i < size; i++) {
        if (arr[i] == value) {
            loc = i; 
            break;   
        }
    }

    if (loc != -1) {
        cout << "Element " << value << " found at position: " << loc << endl;
    } else {
        cout << "Element " << value << " not found." << endl;
    }

    return 0;
}
"""

bubble_sort_asc = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    for (int i = 0; i < size - 1; i++){
        for (int j = 0; j < size - i - 1; j++) {
            if (arr[j] > arr[j + 1]) { // use < for descending order
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""

selection_sort = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    // Selection Sort Algorithm
    for (int i = 0; i < size - 1; i++) {
        
        int min_idx = i;
        for (int j = i + 1; j < size; j++) {
            if (arr[j] < arr[min_idx]){ // use > for descending order
                min_idx = j;
            }
        }

        int temp = arr[min_idx];
        arr[min_idx] = arr[i];
        arr[i] = temp;
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""
stack = """
#include <iostream>
using namespace std;

#define STACK_SIZE 100

int stack[STACK_SIZE];
int top = -1; 

void push(int value) {
    if (top >= STACK_SIZE - 1) {
        cout << "Overflow!" << endl;
    } else {
        top++; 
        stack[top] = value; 
        cout << value << " pushed in stack" << endl;
    }
}

void pop() {
    if (top == -1) {
        cout << "Underflow!" << endl;
    } else {
        int poppedValue = stack[top]; 
        top--; 
        cout << poppedValue << " popped from stack." << endl;
    }
}

void display() {
    if (top == -1) {
        cout << "Empty." << endl;
    } else {
        cout << "Elements in stack:" << endl;
        for (int i = top; i >= 0; i--) {
            cout << stack[i] << endl;
        }
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Push (Add)" << endl;
        cout << "2. Pop (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to push: ";
                cin >> value;
                push(value);
                break;
            case 2:
                pop();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice" << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

insertion_sort = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size;

    cout << "Enter the size of the array: ";
    cin >> size;

    cout << "Enter " << size << " elements: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    // Insertion Sort Algorithm
    for (int i = 1; i < size; i++) {

        int key = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > key) { // invert signs for descending order
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }

    cout << "Array sorted in ascending order: " << endl;
    for (int i = 0; i < size; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}
"""

linear_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 100
int queue[QUEUE_SIZE];
int front = -1;
int rear = -1;

void enqueue(int value) {
    if (rear >= QUEUE_SIZE - 1) {
        cout << "Overflow!" << endl;
    } else {
        if (front == -1) {
            front = 0;
        }
        rear++;
        queue[rear] = value;
        cout << value << " enqueued to the queue." << endl;
    }
}

void dequeue() {
    if (front == -1 || front > rear) {

        cout << "Queue Underflow!." << endl;
    } else {
        int dequeuedValue = queue[front];
        front++;
        cout << "Dequeued " << dequeuedValue << " from the queue." << endl;
        
        if (front > rear) {
            front = -1;
            rear = -1;
        }
    }
}

void display() {
    if (front == -1 || front > rear) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue:" << endl;
        for (int i = front; i <= rear; i++) {
            cout << queue[i] << " ";
        }
        cout << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Add" << endl;
        cout << "2. Remove" << endl;
        cout << "3. Display" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

circular_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 5 

int queue[QUEUE_SIZE];
int front = -1; 
int rear = -1;  

bool isFull() {
    return (front == (rear + 1) % QUEUE_SIZE);
}

bool isEmpty() {
    return (front == -1);
}

void enqueue(int value) {
    if (isFull()) {
        cout << "Queue Overflow" << endl;
    } else {
        if (isEmpty()) {
            front = 0;
        }
        rear = (rear + 1) % QUEUE_SIZE;
        queue[rear] = value; 
        cout << value << " enqueued to the queue." << endl;
    }
}

void dequeue() {
    if (isEmpty()) {
        cout << "Queue Underflow!" << endl;
    } else {
        int dequeuedValue = queue[front];
        
        if (front == rear) {
            front = -1;
            rear = -1;
        } else {
            front = (front + 1) % QUEUE_SIZE;
        }
        
        cout << "Dequeued " << dequeuedValue << " from the queue." << endl;
    }
}

void display() {
    if (isEmpty()) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue:" << endl;
        cout << "FRONT -> ";
        
        int i = front;
        while (true) {
            cout << queue[i] << " ";
            if (i == rear) {
                break; 
            }
            i = (i + 1) % QUEUE_SIZE;
        }
        
        cout << "<- REAR" << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Enqueue (Add)" << endl;
        cout << "2. Dequeue (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""
prioriy_queue = """
#include <iostream>
using namespace std;

#define QUEUE_SIZE 100

int queue[QUEUE_SIZE];
int front = -1; 
int rear = -1;  

bool isFull() {
    return (rear >= QUEUE_SIZE - 1);
}

bool isEmpty() {
    return (front == -1 || front > rear);
}

void enqueue(int value) {
    if (isFull()) {
        cout << "Queue Overflow!" << endl;
        return;
    }

    if (isEmpty()) {
        front = 0;
        rear = 0;
        queue[0] = value;
    } else {
        int j = rear;
        
        while (j >= front && queue[j] < value) {
            queue[j + 1] = queue[j];
            j--;
        }
        
        queue[j + 1] = value;
        rear++; 
    }
    cout << value << " enqueued to the priority queue." << endl;
}

void dequeue() {
    if (isEmpty()) {
        cout << "Queue Underflow!" << endl;
    } else {
        int dequeuedValue = queue[front];
        
        if (front == rear) {
            front = -1;
            rear = -1;
        } else {
            front++;
        }
        
        cout << "Dequeued " << dequeuedValue << "(highest priority) from the queue." << endl;
    }
}

void display() {
    if (isEmpty()) {
        cout << "Queue is empty." << endl;
    } else {
        cout << "Elements in queue(from highest):" << endl;
        cout << "FRONT -> ";
        for (int i = front; i <= rear; i++) {
            cout << queue[i] << " ";
        }
        cout << "<- REAR" << endl;
    }
}

int main() {
    int choice, value;

    do {
        cout << "1. Enqueue (Add)" << endl;
        cout << "2. Dequeue (Remove)" << endl;
        cout << "3. Display" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to enqueue: ";
                cin >> value;
                enqueue(value);
                break;
            case 2:
                dequeue();
                break;
            case 3:
                display();
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
"""

linked_list = """
#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
};

Node* head = NULL;

void display() {
    if (head == NULL) {
        cout << "The list is empty." << endl;
        return;
    }
    Node* temp = head;
    cout << "List (Head to Tail): HEAD -> ";
    while (temp != NULL) {
        cout << temp->data << " -> ";
        temp = temp->next;
    }
    cout << "NULL" << endl;
}

void insertAtBeginning(int data) {
    Node* newNode = new Node();
    newNode->data = data;
    newNode->next = head;
    head = newNode;
    cout << data << " inserted at the beginning." << endl;
    display();
}

void insertAtEnd(int data) {
    Node* newNode = new Node();
    newNode->data = data;
    newNode->next = NULL; 

    if (head == NULL) {
        head = newNode;
    } else {
        Node* temp = head;
        while (temp->next != NULL) {
            temp = temp->next;
        }
        temp->next = newNode;
    }
    
    cout << data << " inserted at the end." << endl;
    display();
}

void insertAtPosition(int data, int pos) {
    if (pos < 1) {
        cout << "Invalid position. Position must be 1 or greater." << endl;
        return;
    }

    if (pos == 1) {
        insertAtBeginning(data);
        return;
    }

    Node* newNode = new Node();
    newNode->data = data;

    Node* prev = head;
    for (int i = 1; i < pos - 1; i++) {
        if (prev == NULL) {
            cout << "Position " << pos << " is out of bounds." << endl;
            delete newNode; 
            return;
        }
        prev = prev->next;
    }
    if (prev == NULL) {
        cout << "Position " << pos << " is out of bounds." << endl;
        delete newNode;
        return;
    }

    newNode->next = prev->next;
    prev->next = newNode;

    cout << data << " inserted at position " << pos << "." << endl;
    display();
}

void deleteFromBeginning() {
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }
    Node* temp = head;
    head = head->next;
    int deletedValue = temp->data;
    delete temp;

    cout << deletedValue << " deleted from the beginning." << endl;
    display();
}

void deleteFromEnd() {
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }

    Node* temp = head;
    Node* secondLast = NULL;

    if (temp->next == NULL){
        int deletedValue = temp->data;
        delete head;
        head = NULL;
        cout << deletedValue << " deleted from the end." << endl;
        display();
        return;
    }

    while (temp->next != NULL) {
        secondLast = temp;
        temp = temp->next;
    }
    int deletedValue = temp->data;
    secondLast->next = NULL;
    
    delete temp;
    cout << deletedValue << " deleted from the end." << endl;
    display();
}

void deleteFromPosition(int pos) {
    if (pos < 1) {
        cout << "Invalid position. Position must be 1 or greater." << endl;
        return;
    }
    
    if (head == NULL) {
        cout << "List is empty. Cannot delete." << endl;
        return;
    }

    if (pos == 1) {
        deleteFromBeginning();
        return;
    }

    Node* prev = head;
    for (int i = 1; i < pos - 1; i++) {
        if (prev == NULL || prev->next == NULL) {
            cout << "Position " << pos << " is out of bounds." << endl;
            return;
        }
        prev = prev->next;
    }

    if (prev == NULL || prev->next == NULL) {
        cout << "Position " << pos << " is out of bounds." << endl;
        return;
    }

    Node* temp = prev->next;
    prev->next = temp->next;
    
    int deletedValue = temp->data;
    delete temp;
    cout << deletedValue << " deleted from position " << pos << "." << endl;
    display();
}


int main() {
    int choice, value, position;

    do {
        cout << "1. Display List" << endl;
        cout << "2. Insert at Beginning" << endl;
        cout << "3. Insert at End" << endl;
        cout << "4. Insert at Specific Position" << endl;
        cout << "5. Delete from Beginning" << endl;
        cout << "6. Delete from End" << endl;
        cout << "7. Delete from Specific Position" << endl;
        cout << "8. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                display();
                break;
            case 2:
                cout << "Enter value to insert: ";
                cin >> value;
                insertAtBeginning(value);
                break;
            case 3:
                cout << "Enter value to insert: ";
                cin >> value;
                insertAtEnd(value);
                break;
            case 4:
                cout << "Enter value to insert: ";
                cin >> value;
                cout << "Enter position (1-based): ";
                cin >> position;
                insertAtPosition(value, position);
                break;
            case 5:
                deleteFromBeginning();
                break;
            case 6:
                deleteFromEnd();
                break;
            case 7:
                cout << "Enter position to delete (1-based): ";
                cin >> position;
                deleteFromPosition(position);
                break;
            case 8:
                cout << "Exiting program. Goodbye!" << endl;
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 8);

    Node* temp = head;
    while (temp != NULL) {
        Node* toDelete = temp;
        temp = temp->next;
        delete toDelete;
    }
    return 0;
}
"""
# -------------PYTHON------------

prog1_grade = """

print("--Student Grade Calculator---")
print("Please enter marks for 3 subjects.")

# Get marks
mark1 = float(input(f"Enter marks for Subject 1 (out of 100): "))
mark2 = float(input(f"Enter marks for Subject 2 (out of 100): "))
mark3 = float(input(f"Enter marks for Subject 3 (out of 100): "))

# Calculate total and percentage
total_marks = mark1 + mark2 + mark3
percentage = (total_marks / 300) * 100

# Determine grade
if percentage >= 90:
    grade = 'A'
elif percentage >= 80:
    grade = 'B'
elif percentage >= 70:
    grade = 'C'
elif percentage >= 60:
    grade = 'D'
else:
    grade = 'F'

# Display results
print("\n--- Results ---")
print(f"Total Marks: {total_marks:.2f} / 300")
print(f"Percentage:  {percentage:.2f}%")
print(f"Grade:       {grade}")
"""

# Program 2: Find Factors
prog2_factors = """
num = int(input("Enter a positive integer: "))

if num > 0:
    print(f"The factors of {num} are:")
    # Loop from 1 up to and including the number itself
    for i in range(1, num + 1):
        if num % i == 0:
            print(i, end=' ')
    print() # Adds a newline at the end
else:
    print("Please enter a number greater than 0.")
"""

# Program 3: Sum of N Natural Numbers
prog3_sum_natural = """
# Get the value of N from the user
n = int(input("Enter a positive integer 'N': "))

if n < 1:
    print("Please enter a positive integer (1 or greater).")
else:
    # Use the efficient mathematical formula: Sum = N * (N + 1) / 2
    total_sum = n * (n + 1) // 2
    
    print(f"The sum of the first {n} natural numbers is: {total_sum}")
"""

# Program 4: Height Conversion Table
prog4_height_table = """

CM_PER_INCH = 2.54
INCHES_PER_FOOT = 12

print("--- Height Conversion Table ---")
# Print table headers
print(f"{'Feet':<5} {'Inches':<7} | {'Centimeters':>12}")
print("-" * 30)

# Loop for feet (e.g., from 4ft to 6ft)
for feet in range(4, 7):
    # Nested loop for inches (0 to 11)
    for inches in range(0, 12):
        
        # 1. Calculate total inches
        total_inches = (feet * INCHES_PER_FOOT) + inches
        
        # 2. Convert total inches to centimeters
        cm = total_inches * CM_PER_INCH
        
        # Print the formatted row
        print(f"{feet:<5} {inches:<7} | {cm:>12.2f} cm")
"""

# Program 5: Pyramid Pattern
prog5_pyramid = """

rows = int(input("Enter the number of rows for the pyramid: "))

if rows <= 0:
    print("Please enter a positive number of rows.")
else:
    # Loop for each row (from 1 to 'rows')
    for i in range(1, rows + 1):
        
        # 1. Print leading spaces
        num_spaces = rows - i
        print(" " * num_spaces, end="")
        
        # 2. Print stars
        num_stars = 2 * i - 1
        print("*" * num_stars)
"""

# Program 6: Area Calculator Menu
prog6_area_menu = """

import math

def calculate_rectangle_area():
    print("\n-- Area of Rectangle --")
    length = float(input("Enter the length: "))
    width = float(input("Enter the width: "))
    area = length * width
    print(f"The area of the rectangle is: {area:.2f}")

def calculate_square_area():
    print("\n-- Area of Square --")
    side = float(input("Enter the side length: "))
    area = side ** 2
    print(f"The area of the square is: {area:.2f}")

def calculate_circle_area():
    print("\n-- Area of Circle --")
    radius = float(input("Enter the radius: "))
    area = math.pi * (radius ** 2)
    print(f"The area of the circle is: {area:.2f}")

def calculate_triangle_area():
    print("\n-- Area of Triangle --")
    base = float(input("Enter the base: "))
    height = float(input("Enter the height: "))
    area = 0.5 * base * height
    print(f"The area of the triangle is: {area:.2f}")

# Main menu loop
while True:
    print("\n--- Area Calculator Menu ---")
    print("1. Calculate Area of a Rectangle")
    print("2. Calculate Area of a Square")
    print("3. Calculate Area of a Circle")
    print("4. Calculate Area of a Triangle")
    print("5. Exit")
    
    choice = input("Enter your choice (1-5): ")

    if choice == '1':
        calculate_rectangle_area()
    elif choice == '2':
        calculate_square_area()
    elif choice == '3':
        calculate_circle_area()
    elif choice == '4':
        calculate_triangle_area()
    elif choice == '5':
        print("Exiting program. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 5.")
"""

# Program 7: Factorial of a Number
prog7_factorial = """

def calculate_factorial(n):
    '''
    Calculates the factorial of a non-negative integer n.
    '''
    if n < 0:
        return -1  # Factorial is not defined for negative numbers
    elif n == 0:
        return 1  # The factorial of 0 is 1
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

print("--- Factorial Calculator ---")
while True:
    try:
        num = int(input("Enter a non-negative integer: "))
        
        if num < 0:
            print("Factorial is not defined for negative numbers. Please try again.")
        else:
            fact = calculate_factorial(num)
            print(f"The factorial of {num} is: {fact}")
            break
    except ValueError:
        print("Invalid input. Please enter an integer.")
"""

# Program 8: Sum of Factorial Series
prog8_series_sum = """

print("--- Series Sum Calculator (1/1! + 1/2! + ... + 1/n!) ---")

while True:
    try:
        n = int(input("Enter a positive integer 'n': "))
        if n > 0:
            break
        else:
            print("Please enter a number greater than 0.")
    except ValueError:
        print("Invalid input. Please enter an integer.")

total_sum = 0.0
current_factorial = 1
series_terms = [] 

# Loop from 1 to n
for i in range(1, n + 1):
    # Calculate factorial efficiently
    current_factorial *= i
    
    # Calculate the term
    term_value = 1.0 / current_factorial
    
    # Add to the total sum
    total_sum += term_value
    
    # Add the string "1/i!" to our list
    series_terms.append(f"1/{i}!")

# Join all terms with " + " to print the series
series_string = " + ".join(series_terms)

print("\n--- Results ---")
print(f"The series is: {series_string}")
print(f"The sum of the series is: {total_sum}")
"""

# Program 9: List Methods Demonstration
prog9_list_methods = """
# --- Part 1: len(), count(), index(), append() ---
print("--- Part 1: len(), count(), index(), append() ---")

my_list = [10, 30, 20, 40, 30, 50]
print(f"Original list: {my_list}")

length = len(my_list)
print(f"1. len(my_list)     -> {length}")

count_of_30 = my_list.count(30)
print(f"2. my_list.count(30)  -> {count_of_30}")

index_of_20 = my_list.index(20)
print(f"3. my_list.index(20) -> {index_of_20}")

print("4. my_list.append(60)")
my_list.append(60)
print(f"   List after append: {my_list}")


# --- Part 2: insert(), extend(), remove(), pop() ---
print("\n--- Part 2: insert(), extend(), remove(), pop() ---")
print(f"Current list: {my_list}")

print("1. my_list.insert(1, 15)")
my_list.insert(1, 15) # Insert 15 at index 1
print(f"   List after insert: {my_list}")

other_list = [100, 200]
print(f"2. my_list.extend({other_list})")
my_list.extend(other_list)
print(f"   List after extend: {my_list}")

print("3. my_list.remove(30)")
my_list.remove(30) # Removes the first 30
print(f"   List after remove: {my_list}")

print("4. popped_item = my_list.pop(2)") # Pop item at index 2
popped_item = my_list.pop(2)
print(f"   Popped item: {popped_item}")
print(f"   List after pop(2): {my_list}")

print("5. last_item = my_list.pop()")
last_item = my_list.pop()
print(f"   Popped last item: {last_item}")
print(f"   List after pop(): {my_list}")


# --- Part 3: reverse(), sort(), copy(), clear() ---
print("\n--- Part 3: reverse(), sort(), copy(), clear() ---")
print(f"Current list: {my_list}")

print("1. my_list.reverse()")
my_list.reverse()
print(f"   List after reverse: {my_list}")

print("2. my_list.sort()")
my_list.sort()
print(f"   List after sort: {my_list}")

print("3. new_copy = my_list.copy()")
new_copy = my_list.copy()
new_copy.append(999) 
print(f"   Original list: {my_list}")
print(f"   New copy (modified): {new_copy}")

print("4. new_copy.clear()")
new_copy.clear()
print(f"   The new copy is now: {new_copy}")
"""

# Program 10: Even/Odd Lists and Operations
prog10_even_odd = """
def create_even_odd_lists(limit):
    '''
    Creates and returns two lists, one of odd numbers and one of even numbers,
    up to a specified limit (inclusive).
    '''
    odd_numbers = []
    even_numbers = []
    
    for num in range(1, limit + 1):
        if num % 2 == 0:
            even_numbers.append(num)
        else:
            odd_numbers.append(num)
            
    return odd_numbers, even_numbers

print("--- Even and Odd List Sorter ---")
limit = 20  # We will sort numbers from 1 to 20

odd_list, even_list = create_even_odd_lists(limit)

print(f"Sorting numbers from 1 to {limit}...\n")
print(f"Odd Numbers:  {odd_list}")
print(f"Even Numbers: {even_list}")


print("\n--- Demonstrating List Operations ---")

# 1. Concatenation (+)
print("\n1. Concatenation (odd_list + even_list)")
all_numbers = odd_list + even_list
print(f"   Result: {all_numbers}")

# 2. Length (len())
print("\n2. Length (len())")
print(f"   Length of odd_list:  {len(odd_list)}")
print(f"   Length of even_list: {len(even_list)}")

# 3. Slicing ([start:end])
print("\n3. Slicing (even_list[1:4])")
some_evens = even_list[1:4]
print(f"   The 2nd to 4th even numbers are: {some_evens}")

# 4. Membership (in)
print("\n4. Membership (in)")
check_num = 7
if check_num in odd_list:
    print(f"   Is {check_num} in the odd list? Yes.")
else:
    print(f"   Is {check_num} in the odd list? No.")
"""

# Program 11: Cubes Dictionary
prog11_cubes_dict = """

def create_cubes_dictionary():
    '''
    Creates a dictionary where keys are numbers from 1 to 5
    and values are the cubes of the keys.
    (Beginner-friendly version)
    '''
    
    # 1. Start with an empty dictionary
    cubes_dict = {}
    
    # 2. Use a 'for' loop to go through the numbers 1, 2, 3, 4, and 5
    for i in range(1, 6):
        
        # 3. Calculate the cube of the number
        cube_value = i ** 3
        
        # 4. Add the number as the 'key' and its cube as the 'value'
        cubes_dict[i] = cube_value

    # 5. Return the completed dictionary
    return cubes_dict

print("--- Cubes Dictionary Creator (Keys 1-5) ---")

dictionary = create_cubes_dictionary()

print("\nSuccessfully created the dictionary:")
print(dictionary)

print("\nIterating through the dictionary:")
for key, value in dictionary.items():
    print(f"Key: {key}  ->  Value: {value}")
"""

# Program 12: Mobile Number Validator
prog12_mobile_regex = """
import re

def is_valid_mobile_number(number_str):
    '''
    Checks if a given string is a valid 10-digit mobile number.
    '''
    
    # Compile the regular expression pattern
    pattern = re.compile(r"^[6-9]\d{9}$")
    
    # Use the pattern to match the input string
    if pattern.match(number_str):
        return True
    else:
        return False

print("--- 10-Digit Mobile Number Validator ---")

# Get input from the user
mobile_number = input("Enter a mobile number to validate: ")

# Check validity and print the result
if is_valid_mobile_number(mobile_number):
    print(f"'{mobile_number}' is a valid mobile number.")
else:
    print(f"'{mobile_number}' is NOT a valid mobile number.")
    print("Please ensure it is exactly 10 digits and starts with 6, 7, 8, or 9.")
"""

#----------OOPSC++---------------
simple_class_bank_account = """
#include <iostream>
#include <string>
using namespace std;

class BankAccount {
    string accountNumber;
    string accountHolderName;
    double balance;

public:
    BankAccount(string accNum, string name, double bal) {
        accountNumber = accNum;
        accountHolderName = name;
        balance = bal;
    }

    void deposit(double amount) {
        balance += amount;
        cout << "Deposited: " << amount << endl;
    }

    void withdraw(double amount) {
        if (amount <= balance) {
            balance -= amount;
            cout << "Withdrawn: " << amount << endl;
        } else {
            cout << "Insufficient balance!" << endl;
        }
    }

    void display() {
        cout << "Account Number: " << accountNumber << endl;
        cout << "Account Holder: " << accountHolderName << endl;
        cout << "Balance: " << balance << endl;
    }
};

int main() {
    BankAccount acc("123456", "John Doe", 5000.0);
    acc.display();
    acc.deposit(2000);
    acc.withdraw(1500);
    acc.display();
    return 0;
}
"""

simple_class_student = """
#include <iostream>
#include <string>
using namespace std;

class Student {
    int rollNo;
    string name;
    float marks;

public:
    void input() {
        cout << "Enter Roll Number: ";
        cin >> rollNo;
        cout << "Enter Name: ";
        cin.ignore();
        getline(cin, name);
        cout << "Enter Marks: ";
        cin >> marks;
    }

    void display() {
        cout << "Roll Number: " << rollNo << endl;
        cout << "Name: " << name << endl;
        cout << "Marks: " << marks << endl;
    }

    char getGrade() {
        if (marks >= 90) return 'A';
        else if (marks >= 80) return 'B';
        else if (marks >= 70) return 'C';
        else if (marks >= 60) return 'D';
        else return 'F';
    }
};

int main() {
    Student s;
    s.input();
    s.display();
    cout << "Grade: " << s.getGrade() << endl;
    return 0;
}
"""

Derive_class_example = """
#include <iostream>
#include <string>
using namespace std;

class Person {
protected:
    string name;
    int age;

public:
    void inputPerson() {
        cout << "Enter Name: ";
        cin.ignore();
        getline(cin, name);
        cout << "Enter Age: ";
        cin >> age;
    }

    void displayPerson() {
        cout << "Name: " << name << endl;
        cout << "Age: " << age << endl;
    }
};

class Employee : public Person {
    int empId;
    double salary;

public:
    void inputEmployee() {
        inputPerson();
        cout << "Enter Employee ID: ";
        cin >> empId;
        cout << "Enter Salary: ";
        cin >> salary;
    }

    void displayEmployee() {
        displayPerson();
        cout << "Employee ID: " << empId << endl;
        cout << "Salary: " << salary << endl;
    }
};

int main() {
    Employee emp;
    emp.inputEmployee();
    cout << "\\nEmployee Details:" << endl;
    emp.displayEmployee();
    return 0;
}
"""

Multiple_class_example = """
#include <iostream>
using namespace std;

class Mathematics {
protected:
    int mathMarks;

public:
    void inputMathMarks() {
        cout << "Enter Math Marks: ";
        cin >> mathMarks;
    }
};

class Science {
protected:
    int scienceMarks;

public:
    void inputScienceMarks() {
        cout << "Enter Science Marks: ";
        cin >> scienceMarks;
    }
};

class Result : public Mathematics, public Science {
    int totalMarks;

public:
    void calculateTotal() {
        totalMarks = mathMarks + scienceMarks;
    }

    void displayResult() {
        cout << "Math Marks: " << mathMarks << endl;
        cout << "Science Marks: " << scienceMarks << endl;
        cout << "Total Marks: " << totalMarks << endl;
    }
};

int main() {
    Result student;
    student.inputMathMarks();
    student.inputScienceMarks();
    student.calculateTotal();
    cout << "\\nResult:" << endl;
    student.displayResult();
    return 0;
}
"""

Mutilevel_class_example = """
#include <iostream>
#include <string>
using namespace std;

class Animal {
protected:
    string species;

public:
    void inputSpecies() {
        cout << "Enter Species: ";
        cin.ignore();
        getline(cin, species);
    }

    void displaySpecies() {
        cout << "Species: " << species << endl;
    }
};

class Mammal : public Animal {
protected:
    string bloodType;

public:
    void inputBloodType() {
        cout << "Enter Blood Type: ";
        cin >> bloodType;
    }

    void displayMammal() {
        displaySpecies();
        cout << "Blood Type: " << bloodType << endl;
    }
};

class Dog : public Mammal {
    string breed;

public:
    void inputDog() {
        inputSpecies();
        inputBloodType();
        cout << "Enter Breed: ";
        cin.ignore();
        getline(cin, breed);
    }

    void displayDog() {
        displayMammal();
        cout << "Breed: " << breed << endl;
    }
};

int main() {
    Dog dog;
    dog.inputDog();
    cout << "\\nDog Details:" << endl;
    dog.displayDog();
    return 0;
}
"""

hierarchical_class_example = """
#include <iostream>
#include <string>
using namespace std;

class Vehicle {
protected:
    string brand;
    int year;

public:
    void inputVehicle() {
        cout << "Enter Brand: ";
        cin.ignore();
        getline(cin, brand);
        cout << "Enter Year: ";
        cin >> year;
    }

    void displayVehicle() {
        cout << "Brand: " << brand << endl;
        cout << "Year: " << year << endl;
    }
};

class Car : public Vehicle {
    int doors;

public:
    void inputCar() {
        inputVehicle();
        cout << "Enter Number of Doors: ";
        cin >> doors;
    }

    void displayCar() {
        displayVehicle();
        cout << "Doors: " << doors << endl;
    }
};

class Bike : public Vehicle {
    string type;

public:
    void inputBike() {
        inputVehicle();
        cout << "Enter Type (Sports/Cruiser): ";
        cin.ignore();
        getline(cin, type);
    }

    void displayBike() {
        displayVehicle();
        cout << "Type: " << type << endl;
    }
};

int main() {
    Car car;
    Bike bike;
    
    cout << "Enter Car Details:" << endl;
    car.inputCar();
    
    cout << "\\nEnter Bike Details:" << endl;
    bike.inputBike();
    
    cout << "\\nCar Details:" << endl;
    car.displayCar();
    
    cout << "\\nBike Details:" << endl;
    bike.displayBike();
    
    return 0;
}
"""

Function_overloading_example = """
#include <iostream>
using namespace std;

class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }

    double add(double a, double b) {
        return a + b;
    }

    int add(int a, int b, int c) {
        return a + b + c;
    }

    void display(int result) {
        cout << "Integer Result: " << result << endl;
    }

    void display(double result) {
        cout << "Double Result: " << result << endl;
    }
};

int main() {
    Calculator calc;
    
    int intResult = calc.add(10, 20);
    calc.display(intResult);
    
    double doubleResult = calc.add(10.5, 20.3);
    calc.display(doubleResult);
    
    int tripleResult = calc.add(10, 20, 30);
    calc.display(tripleResult);
    
    return 0;
}
"""

derived_multiple_inheritance_example = """
#include <iostream>
#include <string>
using namespace std;

class Student {
protected:
    int rollNo;
    string name;

public:
    void inputStudent() {
        cout << "Enter Roll Number: ";
        cin >> rollNo;
        cout << "Enter Name: ";
        cin.ignore();
        getline(cin, name);
    }

    void displayStudent() {
        cout << "Roll Number: " << rollNo << endl;
        cout << "Name: " << name << endl;
    }
};

class Marks {
protected:
    int marks1, marks2, marks3;

public:
    void inputMarks() {
        cout << "Enter Marks 1: ";
        cin >> marks1;
        cout << "Enter Marks 2: ";
        cin >> marks2;
        cout << "Enter Marks 3: ";
        cin >> marks3;
    }

    void displayMarks() {
        cout << "Marks: " << marks1 << ", " << marks2 << ", " << marks3 << endl;
    }
};

class Result : public Student, public Marks {
    int total;
    float percentage;

public:
    void calculate() {
        total = marks1 + marks2 + marks3;
        percentage = (float)total / 3;
    }

    void displayResult() {
        displayStudent();
        displayMarks();
        cout << "Total: " << total << endl;
        cout << "Percentage: " << percentage << "%" << endl;
    }
};

int main() {
    Result r;
    r.inputStudent();
    r.inputMarks();
    r.calculate();
    cout << "\\nResult:" << endl;
    r.displayResult();
    return 0;
}
"""

operator_overloading_example = """
#include <iostream>
using namespace std;

class Complex {
    int real, imag;

public:
    Complex(int r = 0, int i = 0) {
        real = r;
        imag = i;
    }

    Complex operator + (Complex const &obj) {
        Complex result;
        result.real = real + obj.real;
        result.imag = imag + obj.imag;
        return result;
    }

    void display() {
        cout << real << " + " << imag << "i" << endl;
    }
};

int main() {
    Complex c1(3, 4), c2(5, 6);
    Complex c3 = c1 + c2;
    
    cout << "First Complex Number: ";
    c1.display();
    cout << "Second Complex Number: ";
    c2.display();
    cout << "Sum: ";
    c3.display();
    
    return 0;
}
"""

binary_function_overloading_example = """
#include <iostream>
using namespace std;

class Distance {
    int feet, inches;

public:
    Distance(int f = 0, int i = 0) {
        feet = f;
        inches = i;
    }

    Distance operator + (Distance const &d) {
        Distance result;
        result.inches = inches + d.inches;
        result.feet = feet + d.feet + (result.inches / 12);
        result.inches = result.inches % 12;
        return result;
    }

    Distance operator - (Distance const &d) {
        Distance result;
        int totalInches1 = feet * 12 + inches;
        int totalInches2 = d.feet * 12 + d.inches;
        int diff = totalInches1 - totalInches2;
        result.feet = diff / 12;
        result.inches = diff % 12;
        return result;
    }

    void display() {
        cout << feet << " feet " << inches << " inches" << endl;
    }
};

int main() {
    Distance d1(5, 9), d2(3, 4);
    Distance d3 = d1 + d2;
    Distance d4 = d1 - d2;
    
    cout << "First Distance: ";
    d1.display();
    cout << "Second Distance: ";
    d2.display();
    cout << "Sum: ";
    d3.display();
    cout << "Difference: ";
    d4.display();
    
    return 0;
}
"""

# Binary Search Program (C++)
binary_search = """
#include <iostream>
using namespace std;

int main() {
    int arr[100];
    int size, key;
    int low, high, mid;
    bool found = false;

    cout << "Enter size of array: ";
    cin >> size;

    cout << "Enter elements in sorted order: " << endl;
    for (int i = 0; i < size; i++) {
        cin >> arr[i];
    }

    cout << "Enter element to search: ";
    cin >> key;

    low = 0;
    high = size - 1;

    while (low <= high) {
        mid = (low + high) / 2;

        if (arr[mid] == key) {
            cout << "Element found at position: " << mid << endl;
            found = true;
            break;
        } 
        else if (arr[mid] < key) {
            low = mid + 1;
        } 
        else {
            high = mid - 1;
        }
    }

    if (!found) {
        cout << "Element not found." << endl;
    }

    return 0;
}
"""


answer_dict = {
    "insertelement": insert_element,
    "deleteelement": delete_element,
    "linearsearch": linear_search,
    "bubblesort": bubble_sort_asc,
    "selectionsort": selection_sort,
    "stack": stack,
    "insertionsort": insertion_sort,
    "linearqueue": linear_queue,
    "circularqueue": circular_queue,
    "priorityqueue": prioriy_queue,
    "binarysearch": binary_search,
    "linkedlist": linked_list,
    "grade": prog1_grade,
    "factors": prog2_factors,
    "sumnatural": prog3_sum_natural,
    "heighttable": prog4_height_table,
    "pyramid": prog5_pyramid,
    "areamenu": prog6_area_menu,
    "factorial": prog7_factorial,
    "seriessum": prog8_series_sum,
    "listmethods": prog9_list_methods,
    "evenodd": prog10_even_odd,
    "cubesdict": prog11_cubes_dict,
    "mobileregex": prog12_mobile_regex,
    "bankaccount": simple_class_bank_account,
    "student": simple_class_student,
    "singleinheritance": Derive_class_example,
    "multipleinheritance": Multiple_class_example,
    "multilevelinheritance": Mutilevel_class_example,
    "hierarchicalinheritance": hierarchical_class_example,
    "functionoverloading": Function_overloading_example,
    "derivedmultipleinheritance": derived_multiple_inheritance_example,
    "operatoroverloading": operator_overloading_example,
    "binaryoperatoroverloading": binary_function_overloading_example,
}
