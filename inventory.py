# inventory.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# VIEW INVENTORY
# =========================
def view_inventory():
    print("\n=== Inventory Stock ===")

    query = """
    SELECT item_id, name, category, stock
    FROM menu_items
    ORDER BY item_id
    """

    cursor.execute(query)
    items = cursor.fetchall()

    if len(items) == 0:
        print("No inventory items found.")
        return

    print("-" * 70)
    print(f"{'ID':<10}{'Item Name':<25}{'Category':<20}{'Stock':<10}")
    print("-" * 70)

    for item in items:
        print(
            f"{item[0]:<10}"
            f"{item[1]:<25}"
            f"{item[2]:<20}"
            f"{item[3]:<10}"
        )

    print("-" * 70)


# =========================
# UPDATE STOCK
# =========================
def update_stock():
    print("\n=== Update Stock ===")

    try:
        item_id = int(input("Enter item ID: "))
    except ValueError:
        print("Invalid item ID.")
        return

    # Check if item exists
    check_query = """
    SELECT * FROM menu_items
    WHERE item_id = %s
    """

    cursor.execute(check_query, (item_id,))
    item = cursor.fetchone()

    if item is None:
        print("Item not found.")
        return

    print(f"\nCurrent Stock for {item[1]}: {item[4]}")

    try:
        new_stock = int(input("Enter new stock quantity: "))

        if new_stock < 0:
            print("Stock cannot be negative.")
            return

    except ValueError:
        print("Invalid stock quantity.")
        return

    update_query = """
    UPDATE menu_items
    SET stock = %s
    WHERE item_id = %s
    """

    cursor.execute(update_query, (new_stock, item_id))
    conn.commit()

    print("Stock updated successfully!")


# =========================
# ADD STOCK
# =========================
def add_stock():
    print("\n=== Add Stock ===")

    try:
        item_id = int(input("Enter item ID: "))
    except ValueError:
        print("Invalid item ID.")
        return

    # Check item exists
    check_query = """
    SELECT * FROM menu_items
    WHERE item_id = %s
    """

    cursor.execute(check_query, (item_id,))
    item = cursor.fetchone()

    if item is None:
        print("Item not found.")
        return

    print(f"Current Stock: {item[4]}")

    try:
        quantity = int(input("Enter quantity to add: "))

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return

    except ValueError:
        print("Invalid quantity.")
        return

    new_stock = item[4] + quantity

    update_query = """
    UPDATE menu_items
    SET stock = %s
    WHERE item_id = %s
    """

    cursor.execute(update_query, (new_stock, item_id))
    conn.commit()

    print("Stock added successfully!")
    print(f"Updated Stock: {new_stock}")


# =========================
# REDUCE STOCK
# =========================
def reduce_stock():
    print("\n=== Reduce Stock ===")

    try:
        item_id = int(input("Enter item ID: "))
    except ValueError:
        print("Invalid item ID.")
        return

    # Check item exists
    check_query = """
    SELECT * FROM menu_items
    WHERE item_id = %s
    """

    cursor.execute(check_query, (item_id,))
    item = cursor.fetchone()

    if item is None:
        print("Item not found.")
        return

    print(f"Current Stock: {item[4]}")

    try:
        quantity = int(input("Enter quantity to reduce: "))

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return

    except ValueError:
        print("Invalid quantity.")
        return

    if quantity > item[4]:
        print("Insufficient stock.")
        return

    new_stock = item[4] - quantity

    update_query = """
    UPDATE menu_items
    SET stock = %s
    WHERE item_id = %s
    """

    cursor.execute(update_query, (new_stock, item_id))
    conn.commit()

    print("Stock reduced successfully!")
    print(f"Updated Stock: {new_stock}")


# =========================
# LOW STOCK ITEMS
# =========================
def low_stock_items():
    print("\n=== Low Stock Items ===")

    try:
        limit = int(input("Enter low stock limit: "))
    except ValueError:
        print("Invalid limit.")
        return

    query = """
    SELECT item_id, name, category, stock
    FROM menu_items
    WHERE stock <= %s
    ORDER BY stock ASC
    """

    cursor.execute(query, (limit,))
    items = cursor.fetchall()

    if len(items) == 0:
        print("No low stock items found.")
        return

    print("-" * 70)
    print(f"{'ID':<10}{'Item Name':<25}{'Category':<20}{'Stock':<10}")
    print("-" * 70)

    for item in items:
        print(
            f"{item[0]:<10}"
            f"{item[1]:<25}"
            f"{item[2]:<20}"
            f"{item[3]:<10}"
        )

    print("-" * 70)


# =========================
# INVENTORY MANAGEMENT MENU
# =========================
def inventory_management():
    while True:
        print("\n========== INVENTORY MANAGEMENT ==========")
        print("1. View Inventory")
        print("2. Update Stock")
        print("3. Add Stock")
        print("4. Reduce Stock")
        print("5. View Low Stock Items")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_inventory()

        elif choice == "2":
            update_stock()

        elif choice == "3":
            add_stock()

        elif choice == "4":
            reduce_stock()

        elif choice == "5":
            low_stock_items()

        elif choice == "6":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")