import sqlite3
import os

DATABASE = "car_rental.db"

if not os.path.exists(DATABASE):
    print("ERROR: car_rental.db file nahi mili!")
    raise SystemExit

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Check whether bookings table exists
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table' AND name = 'bookings'
""")

if cursor.fetchone() is None:
    print("ERROR: bookings table nahi mili.")
    conn.close()
    raise SystemExit

# Show number of existing bookings
cursor.execute("SELECT COUNT(*) FROM bookings")
count = cursor.fetchone()[0]

print(f"Total bookings found: {count}")

confirm = input(
    "Kya tum saari bookings delete karna chahte ho? (yes/no): "
)

if confirm.strip().lower() == "yes":
    cursor.execute("DELETE FROM bookings")
    conn.commit()

    # Reset booking ID counter, if present
    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'bookings'
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    remaining = cursor.fetchone()[0]

    print(f"Bookings remaining: {remaining}")
else:
    print("Deletion cancelled.")

conn.close()
