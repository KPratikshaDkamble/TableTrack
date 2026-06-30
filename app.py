# app.py
# Flask web UI for TableTrack — Restaurant POS System

import os
import csv
import io
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file, jsonify
)
from dotenv import load_dotenv

from db import get_connection, release_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

TAX_RATE = 0.10


def query(sql, params=None, fetch=True, one=False):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        result = None
        if fetch:
            result = cur.fetchone() if one else cur.fetchall()
        else:
            conn.commit()
            if cur.description:
                result = cur.fetchone()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


# =========================================================
# DASHBOARD
# =========================================================
@app.route("/")
def dashboard():
    today_orders, today_sales = query(
        """SELECT COUNT(order_id), COALESCE(SUM(total), 0)
           FROM orders WHERE DATE(order_date) = CURRENT_DATE""",
        one=True,
    )
    month_orders, month_sales = query(
        """SELECT COUNT(order_id), COALESCE(SUM(total), 0)
           FROM orders
           WHERE DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE)""",
        one=True,
    )
    low_stock_count = query(
        "SELECT COUNT(*) FROM menu_items WHERE stock <= 5", one=True
    )[0]
    available_tables_count = query(
        "SELECT COUNT(*) FROM restaurant_tables WHERE LOWER(status) = 'available'",
        one=True,
    )[0]
    total_customers = query("SELECT COUNT(*) FROM customers", one=True)[0]
    total_employees = query("SELECT COUNT(*) FROM employees", one=True)[0]

    recent_orders = query(
        """SELECT o.order_id, c.name, o.status, o.total, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id DESC LIMIT 6"""
    )

    return render_template(
        "dashboard.html",
        today_orders=today_orders, today_sales=today_sales,
        month_orders=month_orders, month_sales=month_sales,
        low_stock_count=low_stock_count,
        available_tables_count=available_tables_count,
        total_customers=total_customers, total_employees=total_employees,
        recent_orders=recent_orders,
    )


# =========================================================
# MENU MANAGEMENT
# =========================================================
@app.route("/menu")
def menu_list():
    search = request.args.get("q", "")
    if search:
        items = query(
            """SELECT * FROM menu_items
               WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(category) LIKE LOWER(%s)
               ORDER BY item_id""",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        items = query("SELECT * FROM menu_items ORDER BY item_id")
    return render_template("menu.html", items=items, search=search)


@app.route("/menu/add", methods=["POST"])
def menu_add():
    name = request.form["name"].strip()
    category = request.form["category"].strip()
    try:
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        if price < 0 or stock < 0 or not name:
            raise ValueError
    except ValueError:
        flash("Invalid menu item details.", "danger")
        return redirect(url_for("menu_list"))

    query(
        "INSERT INTO menu_items (name, category, price, stock) VALUES (%s,%s,%s,%s)",
        (name, category, price, stock), fetch=False,
    )
    flash(f"Menu item '{name}' added.", "success")
    return redirect(url_for("menu_list"))


@app.route("/menu/<int:item_id>/edit", methods=["POST"])
def menu_edit(item_id):
    try:
        price = float(request.form["price"])
        stock = int(request.form["stock"])
    except ValueError:
        flash("Invalid price or stock value.", "danger")
        return redirect(url_for("menu_list"))

    query(
        "UPDATE menu_items SET name=%s, category=%s, price=%s, stock=%s WHERE item_id=%s",
        (request.form["name"], request.form["category"], price, stock, item_id),
        fetch=False,
    )
    flash("Menu item updated.", "success")
    return redirect(url_for("menu_list"))


@app.route("/menu/<int:item_id>/delete", methods=["POST"])
def menu_delete(item_id):
    query("DELETE FROM menu_items WHERE item_id=%s", (item_id,), fetch=False)
    flash("Menu item deleted.", "success")
    return redirect(url_for("menu_list"))


# =========================================================
# CUSTOMER MANAGEMENT
# =========================================================
@app.route("/customers")
def customer_list():
    search = request.args.get("q", "")
    if search:
        customers = query(
            """SELECT * FROM customers
               WHERE LOWER(name) LIKE LOWER(%s) OR phone LIKE %s
               ORDER BY customer_id""",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        customers = query("SELECT * FROM customers ORDER BY customer_id")
    return render_template("customers.html", customers=customers, search=search)


@app.route("/customers/add", methods=["POST"])
def customer_add():
    name = request.form["name"].strip()
    phone = request.form["phone"].strip()
    if not name or not phone:
        flash("Name and phone are required.", "danger")
        return redirect(url_for("customer_list"))
    query("INSERT INTO customers (name, phone) VALUES (%s,%s)", (name, phone), fetch=False)
    flash(f"Customer '{name}' added.", "success")
    return redirect(url_for("customer_list"))


@app.route("/customers/<int:customer_id>/edit", methods=["POST"])
def customer_edit(customer_id):
    query(
        "UPDATE customers SET name=%s, phone=%s WHERE customer_id=%s",
        (request.form["name"], request.form["phone"], customer_id),
        fetch=False,
    )
    flash("Customer updated.", "success")
    return redirect(url_for("customer_list"))


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def customer_delete(customer_id):
    query("DELETE FROM customers WHERE customer_id=%s", (customer_id,), fetch=False)
    flash("Customer deleted.", "success")
    return redirect(url_for("customer_list"))


@app.route("/customers/<int:customer_id>/history")
def customer_history(customer_id):
    customer = query("SELECT * FROM customers WHERE customer_id=%s", (customer_id,), one=True)
    if customer is None:
        flash("Customer not found.", "danger")
        return redirect(url_for("customer_list"))
    orders = query(
        """SELECT order_id, total, status, order_date FROM orders
           WHERE customer_id=%s ORDER BY order_date DESC""",
        (customer_id,),
    )
    return render_template("customer_history.html", customer=customer, orders=orders)


# =========================================================
# EMPLOYEE MANAGEMENT
# =========================================================
@app.route("/employees")
def employee_list():
    role = request.args.get("role", "")
    search = request.args.get("q", "")
    if role:
        employees = query(
            "SELECT * FROM employees WHERE LOWER(role)=LOWER(%s) ORDER BY employee_id", (role,)
        )
    elif search:
        employees = query(
            """SELECT * FROM employees
               WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(role) LIKE LOWER(%s)
               ORDER BY employee_id""",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        employees = query("SELECT * FROM employees ORDER BY employee_id")
    return render_template("employees.html", employees=employees, search=search, role=role)


@app.route("/employees/add", methods=["POST"])
def employee_add():
    name = request.form["name"].strip()
    role = request.form["role"].strip()
    try:
        salary = float(request.form["salary"])
        if salary < 0 or not name or not role:
            raise ValueError
    except ValueError:
        flash("Invalid employee details.", "danger")
        return redirect(url_for("employee_list"))
    query(
        "INSERT INTO employees (name, role, salary) VALUES (%s,%s,%s)",
        (name, role, salary), fetch=False,
    )
    flash(f"Employee '{name}' added.", "success")
    return redirect(url_for("employee_list"))


@app.route("/employees/<int:employee_id>/edit", methods=["POST"])
def employee_edit(employee_id):
    try:
        salary = float(request.form["salary"])
    except ValueError:
        flash("Invalid salary.", "danger")
        return redirect(url_for("employee_list"))
    query(
        "UPDATE employees SET name=%s, role=%s, salary=%s WHERE employee_id=%s",
        (request.form["name"], request.form["role"], salary, employee_id),
        fetch=False,
    )
    flash("Employee updated.", "success")
    return redirect(url_for("employee_list"))


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def employee_delete(employee_id):
    query("DELETE FROM employees WHERE employee_id=%s", (employee_id,), fetch=False)
    flash("Employee deleted.", "success")
    return redirect(url_for("employee_list"))


# =========================================================
# INVENTORY MANAGEMENT
# =========================================================
@app.route("/inventory")
def inventory_list():
    low_only = request.args.get("low") == "1"
    if low_only:
        items = query(
            """SELECT item_id, name, category, stock FROM menu_items
               WHERE stock <= 5 ORDER BY stock ASC"""
        )
    else:
        items = query(
            "SELECT item_id, name, category, stock FROM menu_items ORDER BY item_id"
        )
    return render_template("inventory.html", items=items, low_only=low_only)


@app.route("/inventory/<int:item_id>/adjust", methods=["POST"])
def inventory_adjust(item_id):
    action = request.form["action"]
    try:
        amount = int(request.form["amount"])
    except ValueError:
        flash("Invalid quantity.", "danger")
        return redirect(url_for("inventory_list"))

    item = query("SELECT stock FROM menu_items WHERE item_id=%s", (item_id,), one=True)
    if item is None:
        flash("Item not found.", "danger")
        return redirect(url_for("inventory_list"))

    current = item[0]
    if action == "set":
        new_stock = amount
    elif action == "add":
        new_stock = current + amount
    elif action == "reduce":
        new_stock = current - amount
    else:
        flash("Unknown action.", "danger")
        return redirect(url_for("inventory_list"))

    if new_stock < 0:
        flash("Stock cannot go negative.", "danger")
        return redirect(url_for("inventory_list"))

    query("UPDATE menu_items SET stock=%s WHERE item_id=%s", (new_stock, item_id), fetch=False)
    flash("Stock updated.", "success")
    return redirect(url_for("inventory_list"))


# =========================================================
# TABLE MANAGEMENT
# =========================================================
@app.route("/tables")
def table_list():
    status = request.args.get("status", "")
    if status:
        tables = query(
            "SELECT * FROM restaurant_tables WHERE LOWER(status)=LOWER(%s) ORDER BY table_id",
            (status,),
        )
    else:
        tables = query("SELECT * FROM restaurant_tables ORDER BY table_id")
    return render_template("tables.html", tables=tables, status=status)


@app.route("/tables/add", methods=["POST"])
def table_add():
    try:
        capacity = int(request.form["capacity"])
        if capacity <= 0:
            raise ValueError
    except ValueError:
        flash("Invalid capacity.", "danger")
        return redirect(url_for("table_list"))
    query(
        "INSERT INTO restaurant_tables (capacity, status) VALUES (%s, 'Available')",
        (capacity,), fetch=False,
    )
    flash("Table added.", "success")
    return redirect(url_for("table_list"))


@app.route("/tables/<int:table_id>/status", methods=["POST"])
def table_status(table_id):
    new_status = request.form["status"]
    if new_status not in ("Available", "Occupied", "Reserved"):
        flash("Invalid status.", "danger")
        return redirect(url_for("table_list"))
    query(
        "UPDATE restaurant_tables SET status=%s WHERE table_id=%s",
        (new_status, table_id), fetch=False,
    )
    flash("Table status updated.", "success")
    return redirect(url_for("table_list"))


@app.route("/tables/<int:table_id>/delete", methods=["POST"])
def table_delete(table_id):
    query("DELETE FROM restaurant_tables WHERE table_id=%s", (table_id,), fetch=False)
    flash("Table deleted.", "success")
    return redirect(url_for("table_list"))


# =========================================================
# ORDER MANAGEMENT
# =========================================================
@app.route("/orders")
def order_list():
    orders = query(
        """SELECT o.order_id, c.name, o.table_id, o.status, o.total, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id DESC"""
    )
    return render_template("orders.html", orders=orders)


@app.route("/orders/new", methods=["GET"])
def order_new():
    customers = query("SELECT customer_id, name FROM customers ORDER BY name")
    tables = query(
        "SELECT table_id, capacity FROM restaurant_tables WHERE LOWER(status)='available' ORDER BY table_id"
    )
    menu_items = query(
        "SELECT item_id, name, price, stock FROM menu_items WHERE stock > 0 ORDER BY name"
    )
    return render_template(
        "order_new.html", customers=customers, tables=tables, menu_items=menu_items
    )


@app.route("/orders/create", methods=["POST"])
def order_create():
    customer_id = request.form.get("customer_id")
    table_id = request.form.get("table_id")
    item_ids = request.form.getlist("item_id[]")
    quantities = request.form.getlist("quantity[]")

    if not customer_id or not table_id:
        flash("Customer and table are required.", "danger")
        return redirect(url_for("order_new"))

    table = query("SELECT status FROM restaurant_tables WHERE table_id=%s", (table_id,), one=True)
    if table is None or table[0].lower() != "available":
        flash("Selected table is not available.", "danger")
        return redirect(url_for("order_new"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_id, table_id, status, total) VALUES (%s,%s,'Active',0) RETURNING order_id",
            (customer_id, table_id),
        )
        order_id = cur.fetchone()[0]

        total_amount = 0
        items_added = 0

        for item_id, qty in zip(item_ids, quantities):
            if not item_id or not qty:
                continue
            try:
                item_id = int(item_id)
                qty = int(qty)
            except ValueError:
                continue
            if qty <= 0:
                continue

            cur.execute("SELECT price, stock FROM menu_items WHERE item_id=%s", (item_id,))
            item = cur.fetchone()
            if item is None or qty > item[1]:
                continue

            subtotal = float(item[0]) * qty
            total_amount += subtotal
            items_added += 1

            cur.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES (%s,%s,%s,%s)",
                (order_id, item_id, qty, subtotal),
            )
            cur.execute(
                "UPDATE menu_items SET stock = stock - %s WHERE item_id=%s", (qty, item_id)
            )

        if items_added == 0:
            conn.rollback()
            flash("Order needs at least one valid item.", "danger")
            return redirect(url_for("order_new"))

        cur.execute("UPDATE orders SET total=%s WHERE order_id=%s", (total_amount, order_id))
        cur.execute("UPDATE restaurant_tables SET status='Occupied' WHERE table_id=%s", (table_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)

    flash(f"Order #{order_id} created — total ${total_amount:.2f}", "success")
    return redirect(url_for("order_detail", order_id=order_id))


@app.route("/orders/<int:order_id>")
def order_detail(order_id):
    order = query(
        """SELECT o.order_id, c.name, o.table_id, o.status, o.total, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           WHERE o.order_id=%s""",
        (order_id,), one=True,
    )
    if order is None:
        flash("Order not found.", "danger")
        return redirect(url_for("order_list"))
    items = query(
        """SELECT m.name, oi.quantity, m.price, oi.subtotal
           FROM order_items oi JOIN menu_items m ON oi.item_id = m.item_id
           WHERE oi.order_id=%s""",
        (order_id,),
    )
    return render_template("order_detail.html", order=order, items=items)


@app.route("/orders/<int:order_id>/complete", methods=["POST"])
def order_complete(order_id):
    order = query("SELECT table_id, status FROM orders WHERE order_id=%s", (order_id,), one=True)
    if order is None:
        flash("Order not found.", "danger")
        return redirect(url_for("order_list"))
    if order[1].lower() == "completed":
        flash("Order already completed.", "warning")
        return redirect(url_for("order_detail", order_id=order_id))

    query("UPDATE orders SET status='Completed' WHERE order_id=%s", (order_id,), fetch=False)
    query(
        "UPDATE restaurant_tables SET status='Available' WHERE table_id=%s",
        (order[0],), fetch=False,
    )
    flash("Order completed. Table is now available.", "success")
    return redirect(url_for("order_detail", order_id=order_id))


@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def order_cancel(order_id):
    order = query("SELECT table_id FROM orders WHERE order_id=%s", (order_id,), one=True)
    if order is None:
        flash("Order not found.", "danger")
        return redirect(url_for("order_list"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT item_id, quantity FROM order_items WHERE order_id=%s", (order_id,))
        for item_id, qty in cur.fetchall():
            cur.execute("UPDATE menu_items SET stock = stock + %s WHERE item_id=%s", (qty, item_id))
        cur.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
        cur.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
        cur.execute("UPDATE restaurant_tables SET status='Available' WHERE table_id=%s", (order[0],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)

    flash("Order cancelled, stock restored, table freed.", "success")
    return redirect(url_for("order_list"))


# =========================================================
# BILLING
# =========================================================
@app.route("/billing", methods=["GET"])
def billing_home():
    orders = query(
        """SELECT o.order_id, c.name, o.status, o.total
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id DESC"""
    )
    daily = query(
        """SELECT COUNT(order_id), COALESCE(SUM(total),0) FROM orders
           WHERE DATE(order_date) = CURRENT_DATE""", one=True,
    )
    monthly = query(
        """SELECT COUNT(order_id), COALESCE(SUM(total),0) FROM orders
           WHERE DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE)""",
        one=True,
    )
    return render_template("billing.html", orders=orders, daily=daily, monthly=monthly)


@app.route("/billing/<int:order_id>", methods=["GET", "POST"])
def billing_bill(order_id):
    order = query(
        """SELECT o.order_id, c.name, o.table_id, o.total, o.status, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           WHERE o.order_id=%s""",
        (order_id,), one=True,
    )
    if order is None:
        flash("Order not found.", "danger")
        return redirect(url_for("billing_home"))

    items = query(
        """SELECT m.name, oi.quantity, m.price, oi.subtotal
           FROM order_items oi JOIN menu_items m ON oi.item_id = m.item_id
           WHERE oi.order_id=%s""",
        (order_id,),
    )

    discount_percent = 0.0
    if request.method == "POST":
        try:
            discount_percent = float(request.form.get("discount", 0))
            if discount_percent < 0 or discount_percent > 100:
                raise ValueError
        except ValueError:
            flash("Discount must be between 0 and 100.", "danger")
            discount_percent = 0.0

    subtotal = float(order[3])
    discount_amount = subtotal * (discount_percent / 100)
    discounted_total = subtotal - discount_amount
    tax_amount = discounted_total * TAX_RATE
    grand_total = discounted_total + tax_amount

    return render_template(
        "bill_receipt.html", order=order, items=items,
        subtotal=subtotal, discount_percent=discount_percent,
        discount_amount=discount_amount, tax_amount=tax_amount,
        grand_total=grand_total, tax_rate=TAX_RATE,
    )


@app.route("/billing/<int:order_id>/receipt.txt")
def billing_receipt_download(order_id):
    order = query(
        """SELECT o.order_id, c.name, o.table_id, o.total, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           WHERE o.order_id=%s""",
        (order_id,), one=True,
    )
    if order is None:
        flash("Order not found.", "danger")
        return redirect(url_for("billing_home"))

    items = query(
        """SELECT m.name, oi.quantity, m.price, oi.subtotal
           FROM order_items oi JOIN menu_items m ON oi.item_id = m.item_id
           WHERE oi.order_id=%s""",
        (order_id,),
    )

    subtotal = float(order[3])
    tax_amount = subtotal * TAX_RATE
    grand_total = subtotal + tax_amount

    buf = io.StringIO()
    buf.write("=" * 50 + "\n")
    buf.write("         TABLETRACK RECEIPT\n")
    buf.write("=" * 50 + "\n")
    buf.write(f"Order ID     : {order[0]}\n")
    buf.write(f"Customer     : {order[1]}\n")
    buf.write(f"Table Number : {order[2]}\n")
    buf.write(f"Date         : {order[4]}\n")
    buf.write("=" * 50 + "\n")
    buf.write(f"{'Item':<20}{'Qty':<10}{'Price':<10}{'Total'}\n")
    buf.write("-" * 50 + "\n")
    for name, qty, price, sub in items:
        buf.write(f"{name:<20}{qty:<10}${price:<9}${sub}\n")
    buf.write("-" * 50 + "\n")
    buf.write(f"{'Subtotal:':<35}${subtotal:.2f}\n")
    buf.write(f"{'Tax (10%):':<35}${tax_amount:.2f}\n")
    buf.write("=" * 50 + "\n")
    buf.write(f"{'Grand Total:':<35}${grand_total:.2f}\n")
    buf.write("=" * 50 + "\n")
    buf.write("Thank you for visiting!\n")

    mem = io.BytesIO(buf.getvalue().encode("utf-8"))
    return send_file(
        mem, mimetype="text/plain", as_attachment=True,
        download_name=f"receipt_order_{order_id}.txt",
    )


# =========================================================
# REPORTS (CSV export)
# =========================================================
def csv_response(filename, header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    mem = io.BytesIO(buf.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=filename)


@app.route("/reports")
def reports_home():
    return render_template("reports.html")


@app.route("/reports/menu.csv")
def report_menu():
    rows = query("SELECT * FROM menu_items ORDER BY item_id")
    return csv_response("menu_report.csv", ["Item ID", "Name", "Category", "Price", "Stock"], rows)


@app.route("/reports/customers.csv")
def report_customers():
    rows = query("SELECT * FROM customers ORDER BY customer_id")
    return csv_response("customer_report.csv", ["Customer ID", "Name", "Phone"], rows)


@app.route("/reports/employees.csv")
def report_employees():
    rows = query("SELECT * FROM employees ORDER BY employee_id")
    return csv_response("employee_report.csv", ["Employee ID", "Name", "Role", "Salary"], rows)


@app.route("/reports/orders.csv")
def report_orders():
    rows = query(
        """SELECT o.order_id, c.name, o.table_id, o.status, o.total, o.order_date
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id"""
    )
    return csv_response(
        "orders_report.csv",
        ["Order ID", "Customer Name", "Table ID", "Status", "Total", "Order Date"],
        rows,
    )


@app.route("/reports/inventory.csv")
def report_inventory():
    rows = query(
        "SELECT item_id, name, category, stock FROM menu_items ORDER BY stock ASC"
    )
    return csv_response("inventory_report.csv", ["Item ID", "Name", "Category", "Stock"], rows)


# =========================================================
# ANALYTICS DASHBOARD (Chart.js fed by JSON endpoints)
# =========================================================
@app.route("/analytics")
def analytics_home():
    return render_template("analytics.html")


@app.route("/analytics/data/daily-sales")
def data_daily_sales():
    rows = query(
        """SELECT DATE(order_date), SUM(total) FROM orders
           GROUP BY DATE(order_date) ORDER BY DATE(order_date)"""
    )
    return jsonify({
        "labels": [str(r[0]) for r in rows],
        "values": [float(r[1]) for r in rows],
    })


@app.route("/analytics/data/monthly-sales")
def data_monthly_sales():
    rows = query(
        """SELECT TO_CHAR(order_date, 'YYYY-MM'), SUM(total) FROM orders
           GROUP BY TO_CHAR(order_date, 'YYYY-MM') ORDER BY TO_CHAR(order_date, 'YYYY-MM')"""
    )
    return jsonify({"labels": [r[0] for r in rows], "values": [float(r[1]) for r in rows]})


@app.route("/analytics/data/inventory")
def data_inventory():
    rows = query("SELECT name, stock FROM menu_items ORDER BY stock ASC")
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@app.route("/analytics/data/top-items")
def data_top_items():
    rows = query(
        """SELECT m.name, SUM(oi.quantity) FROM order_items oi
           JOIN menu_items m ON oi.item_id = m.item_id
           GROUP BY m.name ORDER BY SUM(oi.quantity) DESC LIMIT 5"""
    )
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@app.route("/analytics/data/top-customers")
def data_top_customers():
    rows = query(
        """SELECT c.name, COUNT(o.order_id) FROM customers c
           LEFT JOIN orders o ON c.customer_id = o.customer_id
           GROUP BY c.name ORDER BY COUNT(o.order_id) DESC LIMIT 10"""
    )
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@app.route("/analytics/data/employee-salary")
def data_employee_salary():
    rows = query("SELECT name, salary FROM employees ORDER BY salary DESC")
    return jsonify({"labels": [r[0] for r in rows], "values": [float(r[1]) for r in rows]})


@app.route("/analytics/data/order-status")
def data_order_status():
    rows = query("SELECT status, COUNT(*) FROM orders GROUP BY status")
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@app.route("/analytics/sales.csv")
def analytics_export_csv():
    rows = query(
        """SELECT order_id, customer_id, table_id, total, status, order_date
           FROM orders ORDER BY order_date"""
    )
    return csv_response(
        "sales_report.csv",
        ["Order ID", "Customer ID", "Table ID", "Total", "Status", "Order Date"],
        rows,
    )


if __name__ == "__main__":
    # use_reloader=False avoids spawning a second process (which would
    # double the DB connection pool's footprint against the shared DB's
    # low connection cap)
    app.run(debug=True, use_reloader=False)
