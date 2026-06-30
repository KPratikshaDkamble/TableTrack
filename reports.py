# reports.py

import csv
from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# EXPORT MENU REPORT
# =========================
def export_menu_report():

    query = """
    SELECT *
    FROM menu_items
    ORDER BY item_id
    """

    cursor.execute(query)
    items = cursor.fetchall()

    if len(items) == 0:
        print("No menu data found.")
        return

    filename = "menu_report.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        # Header
        writer.writerow([
            "Item ID",
            "Name",
            "Category",
            "Price",
            "Stock"
        ])

        # Data
        for item in items:
            writer.writerow(item)

    print(f"Menu report exported successfully as '{filename}'")


# =========================
# EXPORT CUSTOMER REPORT
# =========================
def export_customer_report():

    query = """
    SELECT *
    FROM customers
    ORDER BY customer_id
    """

    cursor.execute(query)
    customers = cursor.fetchall()

    if len(customers) == 0:
        print("No customer data found.")
        return

    filename = "customer_report.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Customer ID",
            "Name",
            "Phone"
        ])

        for customer in customers:
            writer.writerow(customer)

    print(f"Customer report exported successfully as '{filename}'")


# =========================
# EXPORT EMPLOYEE REPORT
# =========================
def export_employee_report():

    query = """
    SELECT *
    FROM employees
    ORDER BY employee_id
    """

    cursor.execute(query)
    employees = cursor.fetchall()

    if len(employees) == 0:
        print("No employee data found.")
        return

    filename = "employee_report.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Employee ID",
            "Name",
            "Role",
            "Salary"
        ])

        for employee in employees:
            writer.writerow(employee)

    print(f"Employee report exported successfully as '{filename}'")


# =========================
# EXPORT ORDERS REPORT
# =========================
def export_orders_report():

    query = """
    SELECT
        o.order_id,
        c.name,
        o.table_id,
        o.status,
        o.total,
        o.order_date
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    ORDER BY o.order_id
    """

    cursor.execute(query)
    orders = cursor.fetchall()

    if len(orders) == 0:
        print("No order data found.")
        return

    filename = "orders_report.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Order ID",
            "Customer Name",
            "Table ID",
            "Status",
            "Total",
            "Order Date"
        ])

        for order in orders:
            writer.writerow(order)

    print(f"Orders report exported successfully as '{filename}'")


# =========================
# EXPORT INVENTORY REPORT
# =========================
def export_inventory_report():

    query = """
    SELECT
        item_id,
        name,
        category,
        stock
    FROM menu_items
    ORDER BY stock ASC
    """

    cursor.execute(query)
    items = cursor.fetchall()

    if len(items) == 0:
        print("No inventory data found.")
        return

    filename = "inventory_report.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Item ID",
            "Name",
            "Category",
            "Stock"
        ])

        for item in items:
            writer.writerow(item)

    print(f"Inventory report exported successfully as '{filename}'")


# =========================
# REPORTS MENU
# =========================
def reports_management():

    while True:

        print("\n========== REPORTS MANAGEMENT ==========")

        print("1. Export Menu Report")
        print("2. Export Customer Report")
        print("3. Export Employee Report")
        print("4. Export Orders Report")
        print("5. Export Inventory Report")
        print("6. Back To Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            export_menu_report()

        elif choice == "2":
            export_customer_report()

        elif choice == "3":
            export_employee_report()

        elif choice == "4":
            export_orders_report()

        elif choice == "5":
            export_inventory_report()

        elif choice == "6":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")