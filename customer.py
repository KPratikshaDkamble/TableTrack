# customer.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# ADD CUSTOMER
# =========================
def add_customer():
    print("\n=== Add Customer ===")

    name = input("Enter customer name: ")
    phone = input("Enter phone number: ")

    if name.strip() == "" or phone.strip() == "":
        print("Name and phone number cannot be empty.")
        return

    query = """
    INSERT INTO customers (name, phone)
    VALUES (%s, %s)
    """

    cursor.execute(query, (name, phone))
    conn.commit()

    print("Customer added successfully!")


# =========================
# VIEW ALL CUSTOMERS
# =========================
def view_customers():
    print("\n=== Customer List ===")

    query = """
    SELECT * FROM customers
    ORDER BY customer_id
    """

    cursor.execute(query)
    customers = cursor.fetchall()

    if len(customers) == 0:
        print("No customers found.")
        return

    print("-" * 50)
    print(f"{'ID':<10}{'Name':<20}{'Phone':<20}")
    print("-" * 50)

    for customer in customers:
        print(f"{customer[0]:<10}{customer[1]:<20}{customer[2]:<20}")

    print("-" * 50)


# =========================
# SEARCH CUSTOMER
# =========================
def search_customer():
    print("\n=== Search Customer ===")

    keyword = input("Enter customer name or phone number: ")

    query = """
    SELECT * FROM customers
    WHERE LOWER(name) LIKE LOWER(%s)
    OR phone LIKE %s
    """

    search_term = f"%{keyword}%"

    cursor.execute(query, (search_term, search_term))
    customers = cursor.fetchall()

    if len(customers) == 0:
        print("No matching customers found.")
        return

    print("-" * 50)
    print(f"{'ID':<10}{'Name':<20}{'Phone':<20}")
    print("-" * 50)

    for customer in customers:
        print(f"{customer[0]:<10}{customer[1]:<20}{customer[2]:<20}")

    print("-" * 50)


# =========================
# UPDATE CUSTOMER
# =========================
def update_customer():
    print("\n=== Update Customer ===")

    try:
        customer_id = int(input("Enter customer ID to update: "))
    except ValueError:
        print("Invalid customer ID.")
        return

    # Check if customer exists
    check_query = """
    SELECT * FROM customers
    WHERE customer_id = %s
    """

    cursor.execute(check_query, (customer_id,))
    customer = cursor.fetchone()

    if customer is None:
        print("Customer not found.")
        return

    print("Leave field empty to keep old value.")

    new_name = input(f"Enter new name ({customer[1]}): ")
    new_phone = input(f"Enter new phone ({customer[2]}): ")

    # Keep old values
    if new_name == "":
        new_name = customer[1]

    if new_phone == "":
        new_phone = customer[2]

    update_query = """
    UPDATE customers
    SET name = %s,
        phone = %s
    WHERE customer_id = %s
    """

    cursor.execute(update_query, (new_name, new_phone, customer_id))
    conn.commit()

    print("Customer updated successfully!")


# =========================
# DELETE CUSTOMER
# =========================
def delete_customer():
    print("\n=== Delete Customer ===")

    try:
        customer_id = int(input("Enter customer ID to delete: "))
    except ValueError:
        print("Invalid customer ID.")
        return

    # Check if customer exists
    check_query = """
    SELECT * FROM customers
    WHERE customer_id = %s
    """

    cursor.execute(check_query, (customer_id,))
    customer = cursor.fetchone()

    if customer is None:
        print("Customer not found.")
        return

    confirm = input(f"Delete customer '{customer[1]}'? (y/n): ")

    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    delete_query = """
    DELETE FROM customers
    WHERE customer_id = %s
    """

    cursor.execute(delete_query, (customer_id,))
    conn.commit()

    print("Customer deleted successfully!")


# =========================
# CUSTOMER ORDER HISTORY
# =========================
def customer_order_history():
    print("\n=== Customer Order History ===")

    try:
        customer_id = int(input("Enter customer ID: "))
    except ValueError:
        print("Invalid customer ID.")
        return

    # Check customer exists
    customer_query = """
    SELECT * FROM customers
    WHERE customer_id = %s
    """

    cursor.execute(customer_query, (customer_id,))
    customer = cursor.fetchone()

    if customer is None:
        print("Customer not found.")
        return

    query = """
    SELECT order_id, total, status, order_date
    FROM orders
    WHERE customer_id = %s
    ORDER BY order_date DESC
    """

    cursor.execute(query, (customer_id,))
    orders = cursor.fetchall()

    print(f"\nCustomer: {customer[1]}")

    if len(orders) == 0:
        print("No order history found.")
        return

    print("-" * 70)
    print(f"{'Order ID':<15}{'Total':<15}{'Status':<15}{'Date':<20}")
    print("-" * 70)

    for order in orders:
        print(f"{order[0]:<15}${order[1]:<14}{order[2]:<15}{str(order[3]):<20}")

    print("-" * 70)


# =========================
# CUSTOMER MANAGEMENT MENU
# =========================
def customer_management():
    while True:
        print("\n========== CUSTOMER MANAGEMENT ==========")
        print("1. Add Customer")
        print("2. View Customers")
        print("3. Search Customer")
        print("4. Update Customer")
        print("5. Delete Customer")
        print("6. Customer Order History")
        print("7. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_customer()

        elif choice == "2":
            view_customers()

        elif choice == "3":
            search_customer()

        elif choice == "4":
            update_customer()

        elif choice == "5":
            delete_customer()

        elif choice == "6":
            customer_order_history()

        elif choice == "7":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")