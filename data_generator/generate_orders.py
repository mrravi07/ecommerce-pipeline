import pandas as pd
import random
from datetime import datetime
import os

os.makedirs("raw_data", exist_ok=True)

data = []

for i in range(100):
    data.append({
        "order_id": random.randint(1000, 9999),
        "product": random.choice(["Mobile", "Laptop", "Shoes"]),
        "price": random.randint(100, 1000),
        "quantity": random.randint(1, 5),
        "timestamp": datetime.now()
    })

df = pd.DataFrame(data)

file_path = "raw_data/orders.csv"

if os.path.exists(file_path):
    df.to_csv(file_path, mode='a', index=False, header=False)
else:
    df.to_csv(file_path, index=False)

print("✅ Data Generated")