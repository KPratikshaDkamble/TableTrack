# employee.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# ADD EMPLOYEE
# =========================
def add_employee():
    print("\n=== Add Employee ===")

    name = input("Enter employee name: ")
    role = input("Enter employee role (Manager/Chef/Waiter/Cashier): ")

    try:
        salary = float(input("Enter employee salary: "))

        if salary < 0:
            print("Salary cannot be negative.")
            return

    except ValueError:
        print("Invalid salary.")
        return

    if name.strip() == "" or role.strip() == "":
        print("Name and role cannot be empty.")
        return

    query = """
    INSERT INTO employees (name, role, salary)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (name, role, salary))
    conn.commit()

    print("Employee added successfully!")


# =========================
# VIEW EMPLOYEES
# =========================
def view_employees():
    print("\n=== Employee List ===")

    query = """
    SELECT * FROM employees
    ORDER BY employee_id
    """

    cursor.execute(query)
    employees = cursor.fetchall()

    if len(employees) == 0:
        print("No employees found.")
        return

    print("-" * 70)
    print(f"{'ID':<10}{'Name':<25}{'Role':<20}{'Salary':<15}")
    print("-" * 70)

    for employee in employees:
        print(
            f"{employee[0]:<10}"
            f"{employee[1]:<25}"
            f"{employee[2]:<20}"
            f"${employee[3]:<15}"
        )

    print("-" * 70)


# =========================
# SEARCH EMPLOYEE
# =========================
def search_employee():
    print("\n=== Search Employee ===")

    keyword = input("Enter employee name or role: ")

    query = """
    SELECT * FROM employees
    WHERE LOWER(name) LIKE LOWER(%s)
    OR LOWER(role) LIKE LOWER(%s)
    """

    search_term = f"%{keyword}%"

    cursor.execute(query, (search_term, search_term))
    employees = cursor.fetchall()

    if len(employees) == 0:
        print("No matching employees found.")
        return

    print("-" * 70)
    print(f"{'ID':<10}{'Name':<25}{'Role':<20}{'Salary':<15}")
    print("-" * 70)

    for employee in employees:
        print(
            f"{employee[0]:<10}"
            f"{employee[1]:<25}"
            f"{employee[2]:<20}"
            f"${employee[3]:<15}"
        )

    print("-" * 70)


# =========================
# UPDATE EMPLOYEE
# =========================
def update_employee():
    print("\n=== Update Employee ===")

    try:
        employee_id = int(input("Enter employee ID to update: "))
    except ValueError:
        print("Invalid employee ID.")
        return

    # Check if employee exists
    check_query = """
    SELECT * FROM employees
    WHERE employee_id = %s
    """

    cursor.execute(check_query, (employee_id,))
    employee = cursor.fetchone()

    if employee is None:
        print("Employee not found.")
        return

    print("Leave field empty to keep old value.")

    new_name = input(f"Enter new name ({employee[1]}): ")
    new_role = input(f"Enter new role ({employee[2]}): ")
    new_salary = input(f"Enter new salary ({employee[3]}): ")

    # Keep old values if empty
    if new_name == "":
        new_name = employee[1]

    if new_role == "":
        new_role = employee[2]

    if new_salary == "":
        new_salary = employee[3]
    else:
        try:
            new_salary = float(new_salary)

            if new_salary < 0:
                print("Salary cannot be negative.")
                return

        except ValueError:
            print("Invalid salary.")
            return

    update_query = """
    UPDATE employees
    SET name = %s,
        role = %s,
        salary = %s
    WHERE employee_id = %s
    """

    cursor.execute(
        update_query,
        (new_name, new_role, new_salary, employee_id)
    )

    conn.commit()

    print("Employee updated successfully!")


# =========================
# DELETE EMPLOYEE
# =========================
def delete_employee():
    print("\n=== Delete Employee ===")

    try:
        employee_id = int(input("Enter employee ID to delete: "))
    except ValueError:
        print("Invalid employee ID.")
        return

    # Check if employee exists
    check_query = """
    SELECT * FROM employees
    WHERE employee_id = %s
    """

    cursor.execute(check_query, (employee_id,))
    employee = cursor.fetchone()

    if employee is None:
        print("Employee not found.")
        return

    confirm = input(f"Delete employee '{employee[1]}'? (y/n): ")

    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    delete_query = """
    DELETE FROM employees
    WHERE employee_id = %s
    """

    cursor.execute(delete_query, (employee_id,))
    conn.commit()

    print("Employee deleted successfully!")


# =========================
# VIEW EMPLOYEES BY ROLE
# =========================
def employees_by_role():
    print("\n=== Employees By Role ===")

    role = input("Enter role to search: ")

    query = """
    SELECT * FROM employees
    WHERE LOWER(role) = LOWER(%s)
    """

    cursor.execute(query, (role,))
    employees = cursor.fetchall()

    if len(employees) == 0:
        print("No employees found for this role.")
        return

    print("-" * 70)
    print(f"{'ID':<10}{'Name':<25}{'Role':<20}{'Salary':<15}")
    print("-" * 70)

    for employee in employees:
        print(
            f"{employee[0]:<10}"
            f"{employee[1]:<25}"
            f"{employee[2]:<20}"
            f"${employee[3]:<15}"
        )

    print("-" * 70)


# =========================
# EMPLOYEE MANAGEMENT MENU
# =========================
def employee_management():
    while True:
        print("\n========== EMPLOYEE MANAGEMENT ==========")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Search Employee")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. View Employees By Role")
        print("7. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_employee()

        elif choice == "2":
            view_employees()

        elif choice == "3":
            search_employee()

        elif choice == "4":
            update_employee()

        elif choice == "5":
            delete_employee()

        elif choice == "6":
            employees_by_role()

        elif choice == "7":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")