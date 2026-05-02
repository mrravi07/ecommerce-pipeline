import pandas as pd
import random
from datetime import datetime, timedelta
from itertools import product

random.seed(42)

# ---------------- BASE WORDS ----------------
brands = [
    "Apple", "Samsung", "OnePlus", "Xiaomi", "Realme", "Sony", "JBL",
    "Dell", "HP", "Lenovo", "Asus", "Acer", "Nike", "Adidas", "Puma",
    "Zara", "H&M", "Boat", "Canon", "Nikon", "LG", "Panasonic"
]

types = [
    "Phone", "Laptop", "Headphones", "Speaker", "Watch",
    "Tablet", "Camera", "TV", "Shoes", "Jacket",
    "T-shirt", "Jeans", "Bag", "Router"
]

models = [
    "Pro", "Max", "Ultra", "Plus", "X", "Air",
    "Mini", "Prime", "Edge", "Neo", "Core", "Elite"
]

# ---------------- CATEGORY ----------------
category_map = {
    "Phone": "Electronics", "Laptop": "Electronics", "Headphones": "Electronics",
    "Speaker": "Electronics", "Watch": "Electronics", "Tablet": "Electronics",
    "Camera": "Electronics", "TV": "Electronics", "Router": "Electronics",

    "Shoes": "Fashion", "Jacket": "Fashion",
    "T-shirt": "Fashion", "Jeans": "Fashion", "Bag": "Fashion"
}

cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"]

# ---------------- PRODUCT GENERATION ----------------
all_combinations = list(product(brands, types, models))
random.shuffle(all_combinations)

products = []
for b, t, m in all_combinations:
    products.append(f"{b} {t} {m}")
    if len(products) == 500:
        break

# ---------------- EXTRA FIELDS ----------------
statuses = ["Placed", "Cancelled", "Shipped", "Delivered"]
reviews = ["Excellent", "Good", "Average", "Bad"]
ratings = [5, 4, 3, 2]

# ---------------- DATA GENERATION ----------------
data = []

for i in range(2000):

    product = random.choice(products)
    product_type = product.split(" ")[1]

    category = category_map.get(product_type, "Other")

    price = random.randint(500, 50000)
    quantity = random.randint(1, 5)

    # ---------------- SCHEDULE ----------------
    is_scheduled = random.choice([True, False])

    if is_scheduled:
        timestamp = datetime.now() + timedelta(days=random.randint(1, 5))
    else:
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30))

    # ---------------- STATUS ----------------
    status = random.choice(statuses)

    # ---------------- PROFIT ----------------
    cost = price * random.uniform(0.6, 0.9)
    profit = (price - cost) * quantity

    # ---------------- REVIEW ----------------
    review = random.choice(reviews)
    rating = random.choice(ratings)

    data.append({
        "order_id": i + 1,
        "customer_id": random.randint(1000, 2000),
        "product": product,
        "category": category,
        "price": price,
        "quantity": quantity,
        "city": random.choice(cities),
        "timestamp": timestamp,
        "status": status,
        "is_scheduled": is_scheduled,
        "cost": cost,
        "profit": profit,
        "review": review,
        "rating": rating,
        "revenue": price * quantity
    })

# ---------------- SAVE ----------------
df = pd.DataFrame(data)
df.to_csv("raw_data/orders.csv", index=False)

print("🔥 FULL DATA (Status + Profit + Feedback + 500 Products) GENERATED")