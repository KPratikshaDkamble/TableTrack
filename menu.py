# menu.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# ADD MENU ITEM
# =========================
def add_item():
    print("\n=== Add Menu Item ===")

    name = input("Enter item name: ")
    category = input("Enter category: ")

    try:
        price = float(input("Enter price: "))
        stock = int(input("Enter stock quantity: "))

        if price < 0 or stock < 0:
            print("Price and stock cannot be negative.")
            return

    except ValueError:
        print("Invalid input.")
        return

    query = """
    INSERT INTO menu_items (name, category, price, stock)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (name, category, price, stock))
    conn.commit()

    print("Menu item added successfully!")


# =========================
# VIEW MENU
# =========================
def view_menu():
    print("\n=== Restaurant Menu ===")

    query = """
    SELECT * FROM menu_items
    ORDER BY item_id
    """

    cursor.execute(query)
    items = cursor.fetchall()

    if len(items) == 0:
        print("No menu items found.")
        return

    print("-" * 70)
    print(f"{'ID':<5}{'Name':<20}{'Category':<20}{'Price':<10}{'Stock':<10}")
    print("-" * 70)

    for item in items:
        print(f"{item[0]:<5}{item[1]:<20}{item[2]:<20}${item[3]:<10}{item[4]:<10}")

    print("-" * 70)


# =========================
# SEARCH MENU ITEM
# =========================
def search_item():
    print("\n=== Search Menu Item ===")

    keyword = input("Enter item name or category: ")

    query = """
    SELECT * FROM menu_items
    WHERE LOWER(name) LIKE LOWER(%s)
    OR LOWER(category) LIKE LOWER(%s)
    """

    search_term = f"%{keyword}%"

    cursor.execute(query, (search_term, search_term))
    items = cursor.fetchall()

    if len(items) == 0:
        print("No matching items found.")
        return

    print("-" * 70)
    print(f"{'ID':<5}{'Name':<20}{'Category':<20}{'Price':<10}{'Stock':<10}")
    print("-" * 70)

    for item in items:
        print(f"{item[0]:<5}{item[1]:<20}{item[2]:<20}${item[3]:<10}{item[4]:<10}")

    print("-" * 70)


# =========================
# UPDATE MENU ITEM
# =========================
def update_item():
    print("\n=== Update Menu Item ===")

    try:
        item_id = int(input("Enter item ID to update: "))
    except ValueError:
        print("Invalid ID.")
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

    print("Leave field empty to keep current value.")

    new_name = input(f"Enter new name ({item[1]}): ")
    new_category = input(f"Enter new category ({item[2]}): ")
    new_price = input(f"Enter new price ({item[3]}): ")
    new_stock = input(f"Enter new stock ({item[4]}): ")

    # Keep old values if empty
    if new_name == "":
        new_name = item[1]

    if new_category == "":
        new_category = item[2]

    if new_price == "":
        new_price = item[3]
    else:
        try:
            new_price = float(new_price)
        except ValueError:
            print("Invalid price.")
            return

    if new_stock == "":
        new_stock = item[4]
    else:
        try:
            new_stock = int(new_stock)
        except ValueError:
            print("Invalid stock.")
            return

    update_query = """
    UPDATE menu_items
    SET name = %s,
        category = %s,
        price = %s,
        stock = %s
    WHERE item_id = %s
    """

    cursor.execute(
        update_query,
        (new_name, new_category, new_price, new_stock, item_id)
    )

    conn.commit()

    print("Menu item updated successfully!")


# =========================
# DELETE MENU ITEM
# =========================
def delete_item():
    print("\n=== Delete Menu Item ===")

    try:
        item_id = int(input("Enter item ID to delete: "))
    except ValueError:
        print("Invalid ID.")
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

    confirm = input(f"Delete '{item[1]}'? (y/n): ")

    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    delete_query = """
    DELETE FROM menu_items
    WHERE item_id = %s
    """

    cursor.execute(delete_query, (item_id,))
    conn.commit()

    print("Menu item deleted successfully!")


# =========================
# MENU MANAGEMENT SYSTEM
# =========================
def menu_management():
    while True:
        print("\n========== MENU MANAGEMENT ==========")
        print("1. Add Menu Item")
        print("2. View Menu")
        print("3. Search Menu Item")
        print("4. Update Menu Item")
        print("5. Delete Menu Item")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_item()

        elif choice == "2":
            view_menu()

        elif choice == "3":
            search_item()

        elif choice == "4":
            update_item()

        elif choice == "5":
            delete_item()

        elif choice == "6":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")