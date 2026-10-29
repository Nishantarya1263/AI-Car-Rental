
import sqlite3

connection = sqlite3.connect("car_rental.db")
cursor = connection.cursor()

image_urls = {
    # Your existing local Swift image
    "Swift": "https://stimg.cardekho.com/images/car-images/large/Maruti/Swift/9226/1747045535143/223_Pearl-Arctic-White-with-Bluish-Black-roof_e8e8e8_000000.jpg?impolicy=resize&imwidth=420",

    # Online image URLs
    "Baleno": "https://commons.wikimedia.org/wiki/Special:FilePath/2022%20Maruti%20Suzuki%20Baleno%20Alpha%20%28India%29%20front%20view.jpg",
    "Creta": "https://commons.wikimedia.org/wiki/Special:FilePath/2024%20Hyundai%20Creta%201.5%20MPi%20SX%28O%29%20%28India%29%20front%20view.png",
    "Nexon": "https://www.lakshmitata.co.in/blog/wp-content/uploads/2025/07/tata-nexon-suv-indian-roads.webp",
    "Fortuner": "https://stimg.cardekho.com/pwa/img-gallery/toyota-fortuner/01-top01-front-three-quarter-studio-view.jpg",
    "City": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Honda/City/13532/1780294607751/exterior-image-164.jpg",
    "Scorpio N": "https://stimg.cardekho.com/images/car-images/large/Mahindra/Scorpio-N/13746/1785924987591/STEALTH-BLACK_080808.jpg?impolicy=resize&imwidth=420",
    "Seltos": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Kia/Seltos/13094/1778328978290/front-view-118.jpg",
    "Punch EV": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Tata/Punch-EV/13330/1772693950592/front-left-side-47.jpg",
    "Ertiga": "https://stimg.cardekho.com/images/car-images/360x240/Maruti/Ertiga/10288/1760527558211/Arctic-White_c5c5c5.jpg?imwidth=420&impolicy=resize",
}

for model, url in image_urls.items():
    cursor.execute(
        "UPDATE cars SET image_url = ? WHERE model = ?",
        (url, model)
    )

connection.commit()

print("Car image URLs updated!")

cursor.execute("SELECT model, image_url FROM cars")
for row in cursor.fetchall():
    print(row)

connection.close()
