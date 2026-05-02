import pandas as pd
import os

os.makedirs("processed_data", exist_ok=True)

# raw data read
df = pd.read_csv("raw_data/orders.csv")

# duplicate remove
df.drop_duplicates(inplace=True)

# revenue calculate
df["revenue"] = df["price"] * df["quantity"]

# clean data save
df.to_csv("processed_data/clean_orders.csv", index=False)

print("✅ Data Processed Successfully")

