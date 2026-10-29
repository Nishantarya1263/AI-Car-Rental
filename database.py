
import sqlite3

# Connect to the existing database
connection = sqlite3.connect("car_rental.db")
cursor = connection.cursor()

# Reset tables for a fresh project
cursor.execute("DROP TABLE IF EXISTS bookings")
cursor.execute("DROP TABLE IF EXISTS cars")

# Create cars table with image URLs
cursor.execute("""
CREATE TABLE cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    car_type TEXT NOT NULL,
    seats INTEGER NOT NULL,
    fuel TEXT NOT NULL,
    price_per_day INTEGER NOT NULL,
    available INTEGER DEFAULT 1,
    image_url TEXT
)
""")

# Create fresh bookings table
cursor.execute("""
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    car_id INTEGER,
    pickup_date TEXT,
    return_date TEXT,
    total_price INTEGER,
    status TEXT DEFAULT 'Booked',
    FOREIGN KEY (car_id) REFERENCES cars(id)
)
""")

# Indian car catalogue
cars = [
    (
        "Maruti Suzuki", "Swift", "Hatchback",
        5, "Petrol", 1500, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Swift"
    ),
    (
        "Maruti Suzuki", "Baleno", "Hatchback",
        5, "Petrol", 1700, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Baleno"
    ),
    (
        "Hyundai", "Creta", "SUV",
        5, "Petrol", 2500, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Hyundai+Creta"
    ),
    (
        "Tata", "Nexon", "SUV",
        5, "Petrol", 2200, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Tata+Nexon"
    ),
    (
        "Toyota", "Fortuner", "SUV",
        7, "Diesel", 4500, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Toyota+Fortuner"
    ),
    (
        "Honda", "City", "Sedan",
        5, "Petrol", 2300, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Honda+City"
    ),
    (
        "Mahindra", "Scorpio N", "SUV",
        7, "Diesel", 3500, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Scorpio+N"
    ),
    (
        "Kia", "Seltos", "SUV",
        5, "Petrol", 2700, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Kia+Seltos"
    ),
    (
        "Tata", "Punch EV", "SUV",
        5, "Electric", 2400, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Tata+Punch+EV"
    ),
    (
        "Maruti Suzuki", "Ertiga", "MUV",
        7, "Petrol", 2600, 1,
        "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Ertiga"
    )
]

cursor.executemany("""
INSERT INTO cars (
    brand, model, car_type, seats, fuel,
    price_per_day, available, image_url
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", cars)

connection.commit()

# Verify the catalogue
cursor.execute("SELECT COUNT(*) FROM cars")
print("Total cars:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM bookings")
print("Total bookings:", cursor.fetchone()[0])

# Update car image URLs without deleting bookings
image_urls = {
    "Swift": "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Swift",
    "Baleno": "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Baleno",
    "Creta": "https://placehold.co/800x450/eaf1ff/15213a?text=Hyundai+Creta",
    "Nexon": "https://placehold.co/800x450/eaf1ff/15213a?text=Tata+Nexon",
    "Fortuner": "https://placehold.co/800x450/eaf1ff/15213a?text=Toyota+Fortuner",
    "City": "https://placehold.co/800x450/eaf1ff/15213a?text=Honda+City",
    "Scorpio N": "https://placehold.co/800x450/eaf1ff/15213a?text=Scorpio+N",
    "Seltos": "https://placehold.co/800x450/eaf1ff/15213a?text=Kia+Seltos",
    "Punch EV": "https://placehold.co/800x450/eaf1ff/15213a?text=Tata+Punch+EV",
    "Ertiga": "https://placehold.co/800x450/eaf1ff/15213a?text=Maruti+Ertiga"
}

for model, image_url in image_urls.items():
    cursor.execute(
        "UPDATE cars SET image_url = ? WHERE model = ?",
        (image_url, model)
    )

connection.commit()
print("Car image URLs updated!")

connection.close()

print("Database reset successfully!")