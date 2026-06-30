# tables.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()


# =========================
# ADD TABLE
# =========================
def add_table():
    print("\n=== Add Restaurant Table ===")

    try:
        capacity = int(input("Enter table capacity: "))

        if capacity <= 0:
            print("Capacity must be greater than zero.")
            return

    except ValueError:
        print("Invalid capacity.")
        return

    status = "Available"

    query = """
    INSERT INTO restaurant_tables (capacity, status)
    VALUES (%s, %s)
    """

    cursor.execute(query, (capacity, status))
    conn.commit()

    print("Table added successfully!")


# =========================
# VIEW TABLES
# =========================
def view_tables():
    print("\n=== Restaurant Tables ===")

    query = """
    SELECT * FROM restaurant_tables
    ORDER BY table_id
    """

    cursor.execute(query)
    tables = cursor.fetchall()

    if len(tables) == 0:
        print("No tables found.")
        return

    print("-" * 50)
    print(f"{'Table ID':<15}{'Capacity':<15}{'Status':<15}")
    print("-" * 50)

    for table in tables:
        print(
            f"{table[0]:<15}"
            f"{table[1]:<15}"
            f"{table[2]:<15}"
        )

    print("-" * 50)


# =========================
# UPDATE TABLE STATUS
# =========================
def update_table_status():
    print("\n=== Update Table Status ===")

    try:
        table_id = int(input("Enter table ID: "))
    except ValueError:
        print("Invalid table ID.")
        return

    # Check if table exists
    check_query = """
    SELECT * FROM restaurant_tables
    WHERE table_id = %s
    """

    cursor.execute(check_query, (table_id,))
    table = cursor.fetchone()

    if table is None:
        print("Table not found.")
        return

    print("\nAvailable Status Options:")
    print("1. Available")
    print("2. Occupied")
    print("3. Reserved")

    choice = input("Choose new status: ")

    if choice == "1":
        new_status = "Available"

    elif choice == "2":
        new_status = "Occupied"

    elif choice == "3":
        new_status = "Reserved"

    else:
        print("Invalid choice.")
        return

    update_query = """
    UPDATE restaurant_tables
    SET status = %s
    WHERE table_id = %s
    """

    cursor.execute(update_query, (new_status, table_id))
    conn.commit()

    print("Table status updated successfully!")


# =========================
# VIEW AVAILABLE TABLES
# =========================
def available_tables():
    print("\n=== Available Tables ===")

    query = """
    SELECT * FROM restaurant_tables
    WHERE LOWER(status) = 'available'
    ORDER BY table_id
    """

    cursor.execute(query)
    tables = cursor.fetchall()

    if len(tables) == 0:
        print("No available tables.")
        return

    print("-" * 50)
    print(f"{'Table ID':<15}{'Capacity':<15}{'Status':<15}")
    print("-" * 50)

    for table in tables:
        print(
            f"{table[0]:<15}"
            f"{table[1]:<15}"
            f"{table[2]:<15}"
        )

    print("-" * 50)


# =========================
# DELETE TABLE
# =========================
def delete_table():
    print("\n=== Delete Table ===")

    try:
        table_id = int(input("Enter table ID to delete: "))
    except ValueError:
        print("Invalid table ID.")
        return

    # Check if table exists
    check_query = """
    SELECT * FROM restaurant_tables
    WHERE table_id = %s
    """

    cursor.execute(check_query, (table_id,))
    table = cursor.fetchone()

    if table is None:
        print("Table not found.")
        return

    confirm = input(f"Delete Table {table_id}? (y/n): ")

    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    delete_query = """
    DELETE FROM restaurant_tables
    WHERE table_id = %s
    """

    cursor.execute(delete_query, (table_id,))
    conn.commit()

    print("Table deleted successfully!")


# =========================
# SEARCH TABLE BY STATUS
# =========================
def search_table_by_status():
    print("\n=== Search Table By Status ===")

    status = input("Enter status (Available/Occupied/Reserved): ")

    query = """
    SELECT * FROM restaurant_tables
    WHERE LOWER(status) = LOWER(%s)
    ORDER BY table_id
    """

    cursor.execute(query, (status,))
    tables = cursor.fetchall()

    if len(tables) == 0:
        print("No matching tables found.")
        return

    print("-" * 50)
    print(f"{'Table ID':<15}{'Capacity':<15}{'Status':<15}")
    print("-" * 50)

    for table in tables:
        print(
            f"{table[0]:<15}"
            f"{table[1]:<15}"
            f"{table[2]:<15}"
        )

    print("-" * 50)


# =========================
# TABLE MANAGEMENT MENU
# =========================
def table_management():
    while True:
        print("\n========== TABLE MANAGEMENT ==========")
        print("1. Add Table")
        print("2. View Tables")
        print("3. Update Table Status")
        print("4. View Available Tables")
        print("5. Delete Table")
        print("6. Search Table By Status")
        print("7. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_table()

        elif choice == "2":
            view_tables()

        elif choice == "3":
            update_table_status()

        elif choice == "4":
            available_tables()

        elif choice == "5":
            delete_table()

        elif choice == "6":
            search_table_by_status()

        elif choice == "7":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid choice. Please try again.")