# main.py

from menu import menu_management
from customer import customer_management
from employee import employee_management
from inventory import inventory_management
from tables import table_management
from order import order_management
from billing import billing_management
from reports import reports_management
from analytics import analytics_management


# =========================
# MAIN MENU
# =========================
def main():

    while True:

        print("\n" + "=" * 60)
        print("         TABLETRACK")
        print("=" * 60)

        print("1. Menu Management")
        print("2. Customer Management")
        print("3. Employee Management")
        print("4. Inventory Management")
        print("5. Table Management")
        print("6. Order Management")
        print("7. Billing Management")
        print("8. Reports Management")
        print("9. Analytics Dashboard")
        print("10. Exit")

        print("=" * 60)

        choice = input("Enter your choice: ")

        # -------------------------
        # MENU MANAGEMENT
        # -------------------------
        if choice == "1":
            menu_management()

        # -------------------------
        # CUSTOMER MANAGEMENT
        # -------------------------
        elif choice == "2":
            customer_management()

        # -------------------------
        # EMPLOYEE MANAGEMENT
        # -------------------------
        elif choice == "3":
            employee_management()

        # -------------------------
        # INVENTORY MANAGEMENT
        # -------------------------
        elif choice == "4":
            inventory_management()

        # -------------------------
        # TABLE MANAGEMENT
        # -------------------------
        elif choice == "5":
            table_management()

        # -------------------------
        # ORDER MANAGEMENT
        # -------------------------
        elif choice == "6":
            order_management()

        # -------------------------
        # BILLING MANAGEMENT
        # -------------------------
        elif choice == "7":
            billing_management()

        elif choice == "8":
            reports_management()
        
        elif choice == "9":
            analytics_management()

        elif choice == "10":
            print("Thank you for using TableTrack!")
            break

        # -------------------------
        # INVALID CHOICE
        # -------------------------
        else:
            print("Invalid choice. Please try again.")


# =========================
# PROGRAM ENTRY POINT
# =========================
if __name__ == "__main__":
    main()