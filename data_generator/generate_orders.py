import pandas as pd
import random
from datetime import datetime, timedelta
import os

os.makedirs("raw_data", exist_ok=True)

# --------- 500 PRODUCTS GENERATE ---------
products = [f"Product_{i}" for i in range(1, 501)]

# --------- CATEGORIES ---------
category_list = ["Electronics", "Fashion", "Home", "Sports", "Books", "Automobile"]

product_category = {p: random.choice(category_list) for p in products}

# --------- CITIES ---------
cities = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad", "Pune", "Jaipur"]

# --------- DATA GENERATION ---------
data = []

for i in range(2000):  # 👈 BIG DATA (increase kar sakte ho 5000 tak)
    product = random.choice(products)

    data.append({
        "order_id": random.randint(100000, 999999),
        "customer_id": random.randint(1, 1000),
        "product": product,
        "category": product_category[product],
        "price": random.randint(100, 10000),
        "quantity": random.randint(1, 5),
        "city": random.choice(cities),
        "timestamp": datetime.now() - timedelta(days=random.randint(0, 30))
    })

df = pd.DataFrame(data)

file_path = "raw_data/orders.csv"

# append mode
if os.path.exists(file_path):
    df.to_csv(file_path, mode='a', index=False, header=False)
else:
    df.to_csv(file_path, index=False)

print("🔥 BIG DATA (500 Products) Generated Successfully")