import pandas as pd
import numpy as np
import os

# -----------------------------
# 50 US STATES (2-letter codes)
# -----------------------------
states = [
    "CA","TX","NY","FL","WA","IL","PA","OH","GA","NC",
    "MI","NJ","VA","AZ","MA","TN","IN","MO","MD","WI",
    "CO","MN","SC","AL","LA","KY","OR","OK","CT","UT",
    "IA","NV","AR","MS","KS","NM","NE","WV","ID","HI",
    "NH","ME","RI","MT","DE","SD","ND","AK","VT","WY"
]

years = list(range(2010, 2025))

rows = []

np.random.seed(42)

# -----------------------------
# GENERATE DATA
# -----------------------------
for state in states:
    base_price = np.random.randint(180000, 700000)
    base_rent = np.random.randint(900, 2500)
    base_income = np.random.randint(45000, 90000)

    for i, year in enumerate(years):
        growth = 1 + (i * np.random.uniform(0.01, 0.05))

        rows.append({
            "State": state,
            "Year": year,
            "Home_price": int(base_price * growth),
            "Rent": int(base_rent * growth),
            "Income": int(base_income * (1 + i * 0.02))
        })

# -----------------------------
# CREATE DATAFRAME (IMPORTANT FIX)
# -----------------------------
df = pd.DataFrame(rows)

# -----------------------------
# SAVE FILE SAFELY
# -----------------------------
os.makedirs("data", exist_ok=True)

df.to_csv("data/map_dataset.csv", index=False)

print("✅ Dataset saved successfully at data/map_dataset.csv")