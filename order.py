# order.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# CREATE ORDER
# =========================
def create_order():
    print("\n=== Create New Order ===")

    # -------------------------
    # CUSTOMER
    # -------------------------
    try:
        customer_id = int(input("Enter customer ID: "))
    except ValueError:
        print("Invalid customer ID.")
        return

    customer_query = """
    SELECT * FROM customers
    WHERE customer_id = %s
    """

    cursor.execute(customer_query, (customer_id,))
    customer = cursor.fetchone()

    if customer is None:
        print("Customer not found.")
        return

    # -------------------------
    # TABLE
    # -------------------------
    try:
        table_id = int(input("Enter table ID: "))
    except ValueError:
        print("Invalid table ID.")
        return

    table_query = """
    SELECT * FROM restaurant_tables
    WHERE table_id = %s
    """

    cursor.execute(table_query, (table_id,))
    table = cursor.fetchone()

    if table is None:
        print("Table not found.")
        return

    if table[2].lower() != "available":
        print("Table is not available.")
        return

    # -------------------------
    # CREATE EMPTY ORDER
    # -------------------------
    insert_order_query = """
    INSERT INTO orders (customer_id, table_id, status, total)
    VALUES (%s, %s, %s, %s)
    RETURNING order_id
    """

    cursor.execute(
        insert_order_query,
        (customer_id, table_id, "Active", 0)
    )

    order_id = cursor.fetchone()[0]

    total_amount = 0

    print("\n=== Add Items To Order ===")

    while True:

        # -------------------------
        # SHOW MENU
        # -------------------------
        menu_query = """
        SELECT item_id, name, price, stock
        FROM menu_items
        ORDER BY item_id
        """

        cursor.execute(menu_query)
        items = cursor.fetchall()

        print("\nAvailable Menu Items")
        print("-" * 60)
        print(f"{'ID':<10}{'Item':<20}{'Price':<15}{'Stock':<10}")
        print("-" * 60)

        for item in items:
            print(
                f"{item[0]:<10}"
                f"{item[1]:<20}"
                f"${item[2]:<14}"
                f"{item[3]:<10}"
            )

        print("-" * 60)

        # -------------------------
        # SELECT ITEM
        # -------------------------
        try:
            item_id = int(input("Enter item ID (0 to finish): "))
        except ValueError:
            print("Invalid item ID.")
            continue

        if item_id == 0:
            break

        item_query = """
        SELECT * FROM menu_items
        WHERE item_id = %s
        """

        cursor.execute(item_query, (item_id,))
        item = cursor.fetchone()

        if item is None:
            print("Item not found.")
            continue

        # -------------------------
        # QUANTITY
        # -------------------------
        try:
            quantity = int(input("Enter quantity: "))

            if quantity <= 0:
                print("Quantity must be greater than zero.")
                continue

        except ValueError:
            print("Invalid quantity.")
            continue

        current_stock = item[4]

        if quantity > current_stock:
            print("Insufficient stock.")
            continue

        subtotal = item[3] * quantity
        total_amount += subtotal

        # -------------------------
        # INSERT ORDER ITEM
        # -------------------------
        insert_item_query = """
        INSERT INTO order_items (
            order_id,
            item_id,
            quantity,
            subtotal
        )
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            insert_item_query,
            (order_id, item_id, quantity, subtotal)
        )

        # -------------------------
        # UPDATE STOCK
        # -------------------------
        new_stock = current_stock - quantity

        update_stock_query = """
        UPDATE menu_items
        SET stock = %s
        WHERE item_id = %s
        """

        cursor.execute(
            update_stock_query,
            (new_stock, item_id)
        )

        conn.commit()

        print(f"{item[1]} added to order!")

    # -------------------------
    # UPDATE ORDER TOTAL
    # -------------------------
    update_order_query = """
    UPDATE orders
    SET total = %s
    WHERE order_id = %s
    """

    cursor.execute(
        update_order_query,
        (total_amount, order_id)
    )

    # -------------------------
    # UPDATE TABLE STATUS
    # -------------------------
    update_table_query = """
    UPDATE restaurant_tables
    SET status = 'Occupied'
    WHERE table_id = %s
    """

    cursor.execute(update_table_query, (table_id,))

    conn.commit()

    print("\nOrder created successfully!")
    print(f"Order ID: {order_id}")
    print(f"Total Amount: ${total_amount}")


# =========================
# VIEW ORDERS
# =========================
def view_orders():
    print("\n=== All Orders ===")

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
    ORDER BY o.order_id DESC
    """

    cursor.execute(query)
    orders = cursor.fetchall()

    if len(orders) == 0:
        print("No orders found.")
        return

    print("-" * 100)
    print(
        f"{'Order ID':<12}"
        f"{'Customer':<20}"
        f"{'Table':<10}"
        f"{'Status':<15}"
        f"{'Total':<15}"
        f"{'Date'}"
    )
    print("-" * 100)

    for order in orders:
        print(
            f"{order[0]:<12}"
            f"{order[1]:<20}"
            f"{order[2]:<10}"
            f"{order[3]:<15}"
            f"${order[4]:<14}"
            f"{str(order[5])}"
        )

    print("-" * 100)


# =========================
# VIEW ORDER DETAILS
# =========================
def order_details():
    print("\n=== Order Details ===")

    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Invalid order ID.")
        return

    query = """
    SELECT
        m.name,
        oi.quantity,
        oi.subtotal
    FROM order_items oi
    JOIN menu_items m
    ON oi.item_id = m.item_id
    WHERE oi.order_id = %s
    """

    cursor.execute(query, (order_id,))
    items = cursor.fetchall()

    if len(items) == 0:
        print("Order not found.")
        return

    print("-" * 60)
    print(f"{'Item':<25}{'Quantity':<15}{'Subtotal':<15}")
    print("-" * 60)

    total = 0

    for item in items:
        print(
            f"{item[0]:<25}"
            f"{item[1]:<15}"
            f"${item[2]:<15}"
        )

        total += item[2]

    print("-" * 60)
    print(f"Total Amount: ${total}")
    print("-" * 60)


# =========================
# COMPLETE ORDER
# =========================
def complete_order():
    print("\n=== Complete Order ===")

    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Invalid order ID.")
        return

    # Check order exists
    check_query = """
    SELECT table_id, status
    FROM orders
    WHERE order_id = %s
    """

    cursor.execute(check_query, (order_id,))
    order = cursor.fetchone()

    if order is None:
        print("Order not found.")
        return

    if order[1].lower() == "completed":
        print("Order already completed.")
        return

    # Update order status
    update_order_query = """
    UPDATE orders
    SET status = 'Completed'
    WHERE order_id = %s
    """

    cursor.execute(update_order_query, (order_id,))

    # Free table
    update_table_query = """
    UPDATE restaurant_tables
    SET status = 'Available'
    WHERE table_id = %s
    """

    cursor.execute(update_table_query, (order[0],))

    conn.commit()

    print("Order completed successfully!")
    print("Table is now available.")


# =========================
# CANCEL ORDER
# =========================
def cancel_order():
    print("\n=== Cancel Order ===")

    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Invalid order ID.")
        return

    # Check order exists
    check_query = """
    SELECT table_id, status
    FROM orders
    WHERE order_id = %s
    """

    cursor.execute(check_query, (order_id,))
    order = cursor.fetchone()

    if order is None:
        print("Order not found.")
        return

    # Restore stock
    item_query = """
    SELECT item_id, quantity
    FROM order_items
    WHERE order_id = %s
    """

    cursor.execute(item_query, (order_id,))
    items = cursor.fetchall()

    for item in items:

        item_id = item[0]
        quantity = item[1]

        stock_query = """
        UPDATE menu_items
        SET stock = stock + %s
        WHERE item_id = %s
        """

        cursor.execute(stock_query, (quantity, item_id))

    # Delete order items
    delete_items_query = """
    DELETE FROM order_items
    WHERE order_id = %s
    """

    cursor.execute(delete_items_query, (order_id,))

    # Delete order
    delete_order_query = """
    DELETE FROM orders
    WHERE order_id = %s
    """

    cursor.execute(delete_order_query, (order_id,))

    # Free table
    update_table_query = """
    UPDATE restaurant_tables
    SET status = 'Available'
    WHERE table_id = %s
    """

    cursor.execute(update_table_query, (order[0],))

    conn.commit()

    print("Order cancelled successfully!")
    print("Stock restored.")
    print("Table is now available.")


# =========================
# ORDER MANAGEMENT MENU
# =========================
def order_management():
    while True:
        print("\n========== ORDER MANAGEMENT ==========")
        print("1. Create Order")
        print("2. View Orders")
        print("3. View Order Details")
        print("4. Complete Order")
        print("5. Cancel Order")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_order()

        elif choice == "2":
            view_orders()

        elif choice == "3":
            order_details()

        elif choice == "4":
            complete_order()

        elif choice == "5":
            cancel_order()

        elif choice == "6":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")