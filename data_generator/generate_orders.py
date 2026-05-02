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

# ---------------- EXTRA ----------------
statuses = ["Placed", "Cancelled", "Shipped", "Delivered"]

# -------- REVIEW POOLS --------
positive_reviews = [
    "Amazing product!", "Loved it!", "Highly recommended!", "Superb quality!",
    "Excellent performance", "Worth every penny", "Very satisfied", "Top notch quality",
    "Fantastic experience", "Best purchase ever"
]

neutral_reviews = [
    "Average experience", "Okay product", "Not bad", "Works fine",
    "Decent quality", "Could be better", "Just okay", "Nothing special"
]

negative_reviews = [
    "Not satisfied", "Bad experience", "Waste of money", "Very poor quality",
    "Disappointed", "Not worth it", "Terrible product", "Will not recommend"
]

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

    # ---------------- SMART RATING + REVIEW ----------------
    rating = random.randint(1, 5)

    if rating >= 4:
        review = random.choice(positive_reviews)
    elif rating == 3:
        review = random.choice(neutral_reviews)
    else:
        review = random.choice(negative_reviews)

    # ---------------- DATA APPEND ----------------
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
        "cost": round(cost, 2),
        "profit": round(profit, 2),
        "rating": rating,
        "review": review,
        "revenue": price * quantity
    })

# ---------------- SAVE ----------------
df = pd.DataFrame(data)
df.to_csv("raw_data/orders.csv", index=False)

print("🔥 FINAL DATA GENERATED (500 Products + Status + Profit + Smart Reviews)")