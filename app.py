
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "car_rental.db"


# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------------
# CREATE BOOKINGS TABLE
# ----------------------------------
def create_booking_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            car_id INTEGER NOT NULL,
            pickup_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'Booked'
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------------
# CHECK CAR AVAILABILITY FOR DATES
# ----------------------------------
def is_car_available(
    conn, car_id, pickup_date,
    return_date, exclude_booking_id=None
):
    query = """
        SELECT COUNT(*)
        FROM bookings
        WHERE car_id = ?
          AND status != 'Cancelled'
          AND pickup_date < ?
          AND return_date > ?
    """

    params = [car_id, return_date, pickup_date]

    if exclude_booking_id is not None:
        query += " AND id != ?"
        params.append(exclude_booking_id)

    result = conn.execute(query, params).fetchone()[0]

    return result == 0


# ----------------------------------
# HOME PAGE
# ----------------------------------

@app.route("/")
def home():
    return redirect("/login")


# ----------------------------------
# CARS PAGE
# ----------------------------------
@app.route("/cars")
def cars():
    conn = get_db_connection()

    cars_list = conn.execute("""
        SELECT *
        FROM cars
        WHERE available = 1
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("cars.html", cars=cars_list)


# ----------------------------------
# BOOKING PAGE
# ----------------------------------
@app.route("/booking")
def booking_page():
    selected_car_id = request.args.get("car_id", type=int)

    conn = get_db_connection()

    cars = conn.execute("""
        SELECT *
        FROM cars
        WHERE available = 1
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "booking.html",
        cars=cars,
        selected_car_id=selected_car_id
    )


# ----------------------------------
# BOOK A CAR
# ----------------------------------
@app.route("/book", methods=["POST"])
def book():
    customer_name = request.form.get(
        "customer_name", ""
    ).strip()

    mobile = request.form.get(
        "mobile", ""
    ).strip()

    car_id = request.form.get(
        "car_id", ""
    ).strip()

    pickup_date = request.form.get(
        "pickup_date", ""
    ).strip()

    return_date = request.form.get(
        "return_date", ""
    ).strip()

    if not all([
        customer_name, mobile, car_id,
        pickup_date, return_date
    ]):
        return "Please fill in all booking details.", 400

    try:
        car_id = int(car_id)

        pickup = datetime.strptime(
            pickup_date, "%Y-%m-%d"
        ).date()

        returning = datetime.strptime(
            return_date, "%Y-%m-%d"
        ).date()

    except ValueError:
        return "Invalid car ID or date format.", 400

    if returning <= pickup:
        return "Return date must be after pickup date.", 400

    days = (returning - pickup).days

    conn = get_db_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        car = conn.execute("""
            SELECT *
            FROM cars
            WHERE id = ? AND available = 1
        """, (car_id,)).fetchone()

        if car is None:
            conn.rollback()
            return "This car is not available for rental.", 404

        available = is_car_available(
            conn, car_id, pickup_date, return_date
        )

        if not available:
            conn.rollback()
            return (
                "Sorry! This car is already booked "
                "for some or all of your selected dates. "
                "Please choose different dates or another car."
            ), 409

        total_price = days * car["price_per_day"]

        conn.execute("""
            INSERT INTO bookings (
                customer_name,
                mobile,
                car_id,
                pickup_date,
                return_date,
                total_price,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Booked')
        """, (
            customer_name,
            mobile,
            car_id,
            pickup_date,
            return_date,
            total_price
        ))

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Booking could not be saved.")
        return "Booking could not be completed. Please try again.", 500

    finally:
        conn.close()

    return redirect(url_for("my_bookings"))


# ----------------------------------
# MY BOOKINGS PAGE
# ----------------------------------
@app.route("/my-bookings")
def my_bookings():
    conn = get_db_connection()

    bookings = conn.execute("""
        SELECT bookings.*, cars.brand, cars.model
        FROM bookings
        LEFT JOIN cars ON bookings.car_id = cars.id
        ORDER BY bookings.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )


# ----------------------------------
# ADMIN DASHBOARD
# ----------------------------------
@app.route("/admin")

# ----------------------------------
# MANAGE CAR AVAILABILITY
# ----------------------------------
@app.route("/manage-cars")
def manage_cars():
    conn = get_db_connection()

    cars = conn.execute("""
        SELECT *
        FROM cars
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("manage_cars.html", cars=cars)


# ----------------------------------
# UPDATE CAR AVAILABILITY
# ----------------------------------
@app.route(
    "/update-car-availability/<int:car_id>",
    methods=["POST"]
)
def update_car_availability(car_id):
    available = request.form.get("available", "")

    if available not in ("0", "1"):
        return "Invalid availability value.", 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE cars
            SET available = ?
            WHERE id = ?
        """, (int(available), car_id))

        conn.commit()

        if cursor.rowcount == 0:
            return "Car not found.", 404

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Car availability update failed.")
        return "Could not update car availability.", 500

    finally:
        conn.close()

    return redirect(url_for("manage_cars"))

def admin():
    conn = get_db_connection()

    bookings = conn.execute("""
        SELECT bookings.*, cars.brand, cars.model
        FROM bookings
        LEFT JOIN cars ON bookings.car_id = cars.id
        ORDER BY bookings.id DESC
    """).fetchall()

    total_bookings = conn.execute("""
        SELECT COUNT(*) FROM bookings
    """).fetchone()[0]

    total_cars = conn.execute("""
        SELECT COUNT(*) FROM cars
    """).fetchone()[0]

    confirmed_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Confirmed'
    """).fetchone()[0]

    pending_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Booked'
    """).fetchone()[0]

    cancelled_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Cancelled'
    """).fetchone()[0]

    total_revenue = conn.execute("""
        SELECT COALESCE(SUM(total_price), 0)
        FROM bookings
        WHERE status != 'Cancelled'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        bookings=bookings,
        total_bookings=total_bookings,
        total_cars=total_cars,
        confirmed_bookings=confirmed_bookings,
        pending_bookings=pending_bookings,
        cancelled_bookings=cancelled_bookings,
        total_revenue=total_revenue
    )


# ----------------------------------
# UPDATE BOOKING STATUS
# ----------------------------------
@app.route(
    "/update_status/<int:booking_id>",
    methods=["POST"]
)
def update_status(booking_id):
    new_status = request.form.get(
        "status", ""
    ).strip()

    allowed_statuses = [
        "Booked", "Confirmed", "Cancelled"
    ]

    if new_status not in allowed_statuses:
        return "Invalid booking status.", 400

    conn = get_db_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        booking = conn.execute("""
            SELECT *
            FROM bookings
            WHERE id = ?
        """, (booking_id,)).fetchone()

        if booking is None:
            conn.rollback()
            return "Booking not found.", 404

        if new_status != "Cancelled":
            available = is_car_available(
                conn,
                booking["car_id"],
                booking["pickup_date"],
                booking["return_date"],
                exclude_booking_id=booking_id
            )

            if not available:
                conn.rollback()
                return (
                    "Cannot activate this booking: "
                    "another active booking overlaps these dates."
                ), 409

        conn.execute("""
            UPDATE bookings
            SET status = ?
            WHERE id = ?
        """, (new_status, booking_id))

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Booking status update failed.")
        return "Status update failed. Please try again.", 500

    finally:
        conn.close()

    return redirect(url_for("admin"))


# ----------------------------------
# AI CAR RECOMMENDATIONS
# ----------------------------------



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()

    cars = conn.execute("""
        SELECT *
        FROM cars
        WHERE available = 1
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", cars=cars)


@app.route("/recommend-cars", methods=["POST"])
def recommend_cars():
    try:
        budget = int(request.form.get("budget", 0))
    except ValueError:
        return "Please select a valid budget.", 400

    car_type = request.form.get("car_type", "Any")
    fuel = request.form.get("fuel", "Any")

    conn = get_db_connection()

    try:
        cars = conn.execute("""
            SELECT *
            FROM cars
            WHERE available = 1
              AND price_per_day <= ?
            ORDER BY price_per_day ASC
        """, (budget,)).fetchall()
    finally:
        conn.close()

    recommendations = []

    for car in cars:
        if car_type != "Any" and car["car_type"] != car_type:
            continue

        if fuel != "Any" and car["fuel"] != fuel:
            continue

        recommendations.append(car)

    return render_template(
        "recommendation_results.html",
        recommendations=recommendations,
        budget=budget,
        car_type=car_type,
        fuel=fuel
    )


# ----------------------------------
# START APPLICATION
# ----------------------------------
if __name__ == "__main__":
    create_booking_table()
    app.run(debug=True)