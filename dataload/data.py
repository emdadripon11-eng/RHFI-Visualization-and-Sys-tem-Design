# real_estate_pipeline.py

import ssl
import certifi
import pandas as pd
import numpy as np
import requests
import io

# SSL FIX

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())


# SAFE DOWNLOAD FUNCTION

def load_csv(url, name):
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, timeout=30, verify=True)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"❌ Failed to load {name}: {e}")
        return pd.DataFrame()


# 1. DOWNLOAD DATASETS

def load_datasets():
    zillow_url = "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    rent_url = "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_month.csv"
    income_url = "https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv"
    employment_url = "https://raw.githubusercontent.com/datasets/unemployment-us/master/data/unemployment-us.csv"

    zillow = load_csv(zillow_url, "Zillow Prices")
    rent = load_csv(rent_url, "Rent Data")
    income = load_csv(income_url, "Income Data")
    employment = load_csv(employment_url, "Employment Data")

    return zillow, rent, income, employment


# 2. CLEAN DATASETS

def clean_data(zillow, rent, income, employment):
    print("Cleaning datasets...")

    # ---- Zillow ----
    if not zillow.empty:
        zillow['RegionName'] = zillow['RegionName'].astype(str)

        zillow = zillow.melt(id_vars=['RegionName'], var_name='Date', value_name='Home_price')
        zillow['Date'] = pd.to_datetime(zillow['Date'], format='%Y-%m-%d', errors='coerce')

        zillow = zillow.dropna()

        zillow['Home_price'] = (zillow['Home_price'] - zillow['Home_price'].min()) / \
                               (zillow['Home_price'].max() - zillow['Home_price'].min())

    # ---- Rent ----
    if not rent.empty:
        rent['RegionName'] = rent['RegionName'].astype(str)

        rent = rent.melt(id_vars=['RegionName'], var_name='Date', value_name='Rent')
        rent['Date'] = pd.to_datetime(rent['Date'], format='%Y-%m-%d', errors='coerce')

        rent = rent.dropna()

        rent['Rent'] = (rent['Rent'] - rent['Rent'].min()) / \
                       (rent['Rent'].max() - rent['Rent'].min())

    # ---- Income ---- (state-level proxy)
    if not income.empty:
        income = income.rename(columns={'state': 'RegionName', 'total exports': 'Income'})
        income['RegionName'] = income['RegionName'].astype(str)

        income['Date'] = pd.to_datetime('2011-01-01')
        income = income[['RegionName', 'Date', 'Income']]

        income['Income'] = (income['Income'] - income['Income'].min()) / \
                           (income['Income'].max() - income['Income'].min())

    # ---- Employment ---- (unemployment rate proxy)
    if not employment.empty:
        employment = employment.rename(columns={
            'Date': 'Date',
            'Value': 'Employment'
        })

        employment['Date'] = pd.to_datetime(employment['Date'], errors='coerce')
        employment = employment.dropna()

        # Normalize
        employment['Employment'] = (employment['Employment'] - employment['Employment'].min()) / \
                                   (employment['Employment'].max() - employment['Employment'].min())

    print("Cleaning complete!")
    return zillow, rent, income, employment


# 3. MERGE DATASETS

def merge_data(zillow, rent, income, employment):
    print("Merging datasets...")

    df = zillow.copy()

    # Merge rent (ZIP-level)
    if not rent.empty:
        df = pd.merge(df, rent, on=['RegionName', 'Date'], how='inner')

    # Merge income (state mismatch → use Date only)
    if not income.empty:
        df = pd.merge(df, income[['Date', 'Income']], on='Date', how='left')

    # Merge employment (time series → Date only)
    if not employment.empty:
        df = pd.merge(df, employment[['Date', 'Employment']], on='Date', how='left')

    df['Year'] = df['Date'].dt.year

    cols = ['RegionName', 'Year', 'Home_price', 'Income', 'Rent', 'Employment']
    df = df[[c for c in cols if c in df.columns]]

    print("Merge complete!")
    return df


# 4. FEATURE ENGINEERING

def create_features(df):
    print("Creating derived variables...")

    df = df.sort_values(by=['RegionName', 'Year'])

    # Prevent division errors
    df['Home_price'] = df['Home_price'].replace(0, np.nan)

    if 'Rent' in df.columns:
        df['Rent'] = df['Rent'].replace(0, np.nan)

    if 'Income' in df.columns:
        df['Income'] = df['Income'].replace(0, np.nan)

    # Ratios
    df['price_income_ratio'] = df['Home_price'] / df['Income']

    # Growth
    df['price_growth'] = df.groupby('RegionName')['Home_price'].pct_change()

    if 'Rent' in df.columns:
        df['rent_growth'] = df.groupby('RegionName')['Rent'].pct_change()

    if 'Employment' in df.columns:
        df['job_growth'] = df.groupby('RegionName')['Employment'].pct_change()

    # Inventory proxy
    df['inventory_change'] = df.groupby('RegionName')['Home_price'].diff()

    # Clean output
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    print("Feature engineering complete!")
    return df


# MAIN PIPELINE

def main():
    zillow, rent, income, employment = load_datasets()

    if zillow.empty:
        print("❌ Zillow dataset failed. Exiting.")
        return

    zillow, rent, income, employment = clean_data(zillow, rent, income, employment)

    df = merge_data(zillow, rent, income, employment)

    df = create_features(df)

    df.to_csv("final_dataset.csv", index=False)

    print("\n✅ Final dataset saved as: final_dataset.csv")
    print(df.head())


# RUN SCRIPT

if __name__ == "__main__":
    main()
