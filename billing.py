# billing.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


TAX_RATE = 0.10


# =========================
# GENERATE BILL
# =========================
def generate_bill():
    print("\n=== Generate Bill ===")

    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Invalid order ID.")
        return

    # -------------------------
    # GET ORDER
    # -------------------------
    order_query = """
    SELECT
        o.order_id,
        c.name,
        o.table_id,
        o.total,
        o.status,
        o.order_date
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    WHERE o.order_id = %s
    """

    cursor.execute(order_query, (order_id,))
    order = cursor.fetchone()

    if order is None:
        print("Order not found.")
        return

    # -------------------------
    # GET ORDER ITEMS
    # -------------------------
    items_query = """
    SELECT
        m.name,
        oi.quantity,
        m.price,
        oi.subtotal
    FROM order_items oi
    JOIN menu_items m
    ON oi.item_id = m.item_id
    WHERE oi.order_id = %s
    """

    cursor.execute(items_query, (order_id,))
    items = cursor.fetchall()

    if len(items) == 0:
        print("No items found for this order.")
        return

    subtotal = float(order[3])

    # -------------------------
    # DISCOUNT
    # -------------------------
    try:
        discount_percent = float(
            input("Enter discount percentage (0 if none): ")
        )

        if discount_percent < 0 or discount_percent > 100:
            print("Discount must be between 0 and 100.")
            return

    except ValueError:
        print("Invalid discount.")
        return

    discount_amount = subtotal * (discount_percent / 100)

    discounted_total = subtotal - discount_amount

    tax_amount = discounted_total * TAX_RATE

    grand_total = discounted_total + tax_amount

    # -------------------------
    # PRINT RECEIPT
    # -------------------------
    print("\n")
    print("=" * 50)
    print("         TABLETRACK RECEIPT")
    print("=" * 50)

    print(f"Order ID     : {order[0]}")
    print(f"Customer     : {order[1]}")
    print(f"Table Number : {order[2]}")
    print(f"Order Status : {order[4]}")
    print(f"Date         : {order[5]}")

    print("=" * 50)

    print(f"{'Item':<20}{'Qty':<10}{'Price':<10}{'Total'}")
    print("-" * 50)

    for item in items:
        print(
            f"{item[0]:<20}"
            f"{item[1]:<10}"
            f"${item[2]:<9}"
            f"${item[3]}"
        )

    print("-" * 50)

    print(f"{'Subtotal:':<35}${subtotal:.2f}")
    print(f"{'Discount:':<35}-${discount_amount:.2f}")
    print(f"{'Tax (10%):':<35}${tax_amount:.2f}")

    print("=" * 50)
    print(f"{'Grand Total:':<35}${grand_total:.2f}")
    print("=" * 50)

    print("Thank you for visiting!")
    print("=" * 50)


# =========================
# SAVE RECEIPT TO FILE
# =========================
def save_receipt():
    print("\n=== Save Receipt ===")

    try:
        order_id = int(input("Enter order ID: "))
    except ValueError:
        print("Invalid order ID.")
        return

    # -------------------------
    # GET ORDER
    # -------------------------
    order_query = """
    SELECT
        o.order_id,
        c.name,
        o.table_id,
        o.total,
        o.order_date
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    WHERE o.order_id = %s
    """

    cursor.execute(order_query, (order_id,))
    order = cursor.fetchone()

    if order is None:
        print("Order not found.")
        return

    # -------------------------
    # GET ITEMS
    # -------------------------
    items_query = """
    SELECT
        m.name,
        oi.quantity,
        m.price,
        oi.subtotal
    FROM order_items oi
    JOIN menu_items m
    ON oi.item_id = m.item_id
    WHERE oi.order_id = %s
    """

    cursor.execute(items_query, (order_id,))
    items = cursor.fetchall()

    subtotal = float(order[3])

    tax_amount = subtotal * TAX_RATE
    grand_total = subtotal + tax_amount

    filename = f"receipt_order_{order_id}.txt"

    with open(filename, "w") as file:

        file.write("=" * 50 + "\n")
        file.write("         TABLETRACK RECEIPT\n")
        file.write("=" * 50 + "\n")

        file.write(f"Order ID     : {order[0]}\n")
        file.write(f"Customer     : {order[1]}\n")
        file.write(f"Table Number : {order[2]}\n")
        file.write(f"Date         : {order[4]}\n")

        file.write("=" * 50 + "\n")

        file.write(
            f"{'Item':<20}{'Qty':<10}{'Price':<10}{'Total'}\n"
        )

        file.write("-" * 50 + "\n")

        for item in items:
            file.write(
                f"{item[0]:<20}"
                f"{item[1]:<10}"
                f"${item[2]:<9}"
                f"${item[3]}\n"
            )

        file.write("-" * 50 + "\n")

        file.write(f"{'Subtotal:':<35}${subtotal:.2f}\n")
        file.write(f"{'Tax (10%):':<35}${tax_amount:.2f}\n")

        file.write("=" * 50 + "\n")

        file.write(f"{'Grand Total:':<35}${grand_total:.2f}\n")

        file.write("=" * 50 + "\n")
        file.write("Thank you for visiting!\n")
        file.write("=" * 50 + "\n")

    print(f"Receipt saved successfully as '{filename}'")


# =========================
# DAILY SALES REPORT
# =========================
def daily_sales_report():
    print("\n=== Daily Sales Report ===")

    query = """
    SELECT
        COUNT(order_id),
        COALESCE(SUM(total), 0)
    FROM orders
    WHERE DATE(order_date) = CURRENT_DATE
    """

    cursor.execute(query)
    report = cursor.fetchone()

    total_orders = report[0]
    total_sales = report[1]

    print("-" * 40)
    print(f"Total Orders Today : {total_orders}")
    print(f"Total Sales Today  : ${total_sales}")
    print("-" * 40)


# =========================
# MONTHLY SALES REPORT
# =========================
def monthly_sales_report():
    print("\n=== Monthly Sales Report ===")

    query = """
    SELECT
        COUNT(order_id),
        COALESCE(SUM(total), 0)
    FROM orders
    WHERE DATE_TRUNC('month', order_date)
    = DATE_TRUNC('month', CURRENT_DATE)
    """

    cursor.execute(query)
    report = cursor.fetchone()

    total_orders = report[0]
    total_sales = report[1]

    print("-" * 40)
    print(f"Total Orders This Month : {total_orders}")
    print(f"Total Sales This Month  : ${total_sales}")
    print("-" * 40)


# =========================
# BILLING MANAGEMENT MENU
# =========================
def billing_management():
    while True:
        print("\n========== BILLING MANAGEMENT ==========")
        print("1. Generate Bill")
        print("2. Save Receipt To File")
        print("3. Daily Sales Report")
        print("4. Monthly Sales Report")
        print("5. Back To Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            generate_bill()

        elif choice == "2":
            save_receipt()

        elif choice == "3":
            daily_sales_report()

        elif choice == "4":
            monthly_sales_report()

        elif choice == "5":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")