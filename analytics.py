# analytics.py

import matplotlib.pyplot as plt
import pandas as pd

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# ==========================================
# DAILY SALES LINE GRAPH
# ==========================================
def daily_sales_graph():

    query = """
    SELECT
        DATE(order_date),
        SUM(total)
    FROM orders
    GROUP BY DATE(order_date)
    ORDER BY DATE(order_date)
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No sales data found.")
        return

    dates = []
    sales = []

    for row in data:
        dates.append(str(row[0]))
        sales.append(float(row[1]))

    plt.figure(figsize=(10, 5))

    plt.plot(dates, sales, marker='o')

    plt.title("Daily Sales")
    plt.xlabel("Date")
    plt.ylabel("Sales ($)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ==========================================
# MONTHLY SALES BAR GRAPH
# ==========================================
def monthly_sales_graph():

    query = """
    SELECT
        TO_CHAR(order_date, 'YYYY-MM'),
        SUM(total)
    FROM orders
    GROUP BY TO_CHAR(order_date, 'YYYY-MM')
    ORDER BY TO_CHAR(order_date, 'YYYY-MM')
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No monthly sales data found.")
        return

    months = []
    totals = []

    for row in data:
        months.append(row[0])
        totals.append(float(row[1]))

    plt.figure(figsize=(10, 5))

    plt.bar(months, totals)

    plt.title("Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")

    plt.tight_layout()

    plt.show()


# ==========================================
# INVENTORY STOCK GRAPH
# ==========================================
def inventory_graph():

    query = """
    SELECT
        name,
        stock
    FROM menu_items
    ORDER BY stock ASC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No inventory data found.")
        return

    item_names = []
    stock_values = []

    for row in data:
        item_names.append(row[0])
        stock_values.append(row[1])

    plt.figure(figsize=(12, 6))

    plt.bar(item_names, stock_values)

    plt.title("Inventory Stock Levels")
    plt.xlabel("Menu Items")
    plt.ylabel("Stock Quantity")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ==========================================
# TOP SELLING ITEMS PIE CHART
# ==========================================
def top_selling_items_graph():

    query = """
    SELECT
        m.name,
        SUM(oi.quantity) AS total_sold
    FROM order_items oi
    JOIN menu_items m
    ON oi.item_id = m.item_id
    GROUP BY m.name
    ORDER BY total_sold DESC
    LIMIT 5
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No top-selling items data found.")
        return

    items = []
    quantities = []

    for row in data:
        items.append(row[0])
        quantities.append(row[1])

    plt.figure(figsize=(8, 8))

    plt.pie(
        quantities,
        labels=items,
        autopct='%1.1f%%'
    )

    plt.title("Top 5 Selling Items")

    plt.tight_layout()

    plt.show()


# ==========================================
# CUSTOMER ORDER GRAPH
# ==========================================
def customer_orders_graph():

    query = """
    SELECT
        c.name,
        COUNT(o.order_id) AS total_orders
    FROM customers c
    LEFT JOIN orders o
    ON c.customer_id = o.customer_id
    GROUP BY c.name
    ORDER BY total_orders DESC
    LIMIT 10
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No customer data found.")
        return

    customers = []
    orders = []

    for row in data:
        customers.append(row[0])
        orders.append(row[1])

    plt.figure(figsize=(12, 6))

    plt.bar(customers, orders)

    plt.title("Top Customers By Orders")
    plt.xlabel("Customers")
    plt.ylabel("Number Of Orders")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ==========================================
# EMPLOYEE SALARY GRAPH
# ==========================================
def employee_salary_graph():

    query = """
    SELECT
        name,
        salary
    FROM employees
    ORDER BY salary DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No employee data found.")
        return

    employees = []
    salaries = []

    for row in data:
        employees.append(row[0])
        salaries.append(float(row[1]))

    plt.figure(figsize=(10, 5))

    plt.bar(employees, salaries)

    plt.title("Employee Salary Distribution")
    plt.xlabel("Employees")
    plt.ylabel("Salary ($)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ==========================================
# ORDER STATUS GRAPH
# ==========================================
def order_status_graph():

    query = """
    SELECT
        status,
        COUNT(*)
    FROM orders
    GROUP BY status
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        print("No order data found.")
        return

    statuses = []
    counts = []

    for row in data:
        statuses.append(row[0])
        counts.append(row[1])

    plt.figure(figsize=(7, 7))

    plt.pie(
        counts,
        labels=statuses,
        autopct='%1.1f%%'
    )

    plt.title("Order Status Distribution")

    plt.tight_layout()

    plt.show()


# ==========================================
# EXPORT SALES REPORT CSV
# ==========================================
def export_sales_csv():

    query = """
    SELECT
        order_id,
        customer_id,
        table_id,
        total,
        status,
        order_date
    FROM orders
    ORDER BY order_date
    """

    df = pd.read_sql(query, conn)

    filename = "sales_report.csv"

    df.to_csv(filename, index=False)

    print(f"Sales report exported successfully as '{filename}'")


# ==========================================
# ANALYTICS MENU
# ==========================================
def analytics_management():

    while True:

        print("\n========== ANALYTICS DASHBOARD ==========")

        print("1. Daily Sales Graph")
        print("2. Monthly Sales Graph")
        print("3. Inventory Graph")
        print("4. Top Selling Items Graph")
        print("5. Customer Orders Graph")
        print("6. Employee Salary Graph")
        print("7. Order Status Graph")
        print("8. Export Sales CSV")
        print("9. Back To Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            daily_sales_graph()

        elif choice == "2":
            monthly_sales_graph()

        elif choice == "3":
            inventory_graph()

        elif choice == "4":
            top_selling_items_graph()

        elif choice == "5":
            customer_orders_graph()

        elif choice == "6":
            employee_salary_graph()

        elif choice == "7":
            order_status_graph()

        elif choice == "8":
            export_sales_csv()

        elif choice == "9":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice.")