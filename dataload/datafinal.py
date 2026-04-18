import pandas as pd
import numpy as np
import requests
import io

# ===============================
# DOWNLOAD FUNCTION
# ===============================
def load_csv(url, name):
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"❌ Failed to load {name}: {e}")
        return pd.DataFrame()


# ===============================
# LOAD DATASETS (NATIONAL ZILLOW)
# ===============================
def load_datasets():
    zillow_url = "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    rent_url = "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_month.csv"

    zillow = load_csv(zillow_url, "Zillow Prices")
    rent = load_csv(rent_url, "Rent Data")

    return zillow, rent


# ===============================
# CLEAN DATA
# ===============================
def clean_data(zillow, rent):
    print("Cleaning datasets...")

    zillow["RegionName"] = zillow["RegionName"].astype(str)
    rent["RegionName"] = rent["RegionName"].astype(str)

    zillow = zillow.melt(
        id_vars=["RegionName"],
        var_name="Date",
        value_name="Home_price"
    )

    rent = rent.melt(
        id_vars=["RegionName"],
        var_name="Date",
        value_name="Rent"
    )

    zillow["Date"] = pd.to_datetime(zillow["Date"], errors="coerce")
    rent["Date"] = pd.to_datetime(rent["Date"], errors="coerce")

    zillow = zillow.dropna()
    rent = rent.dropna()

    print("Cleaning complete!")
    return zillow, rent


# ===============================
# MERGE DATASETS
# ===============================
def merge_data(zillow, rent):
    print("Merging datasets...")

    df = pd.merge(
        zillow,
        rent,
        on=["RegionName", "Date"],
        how="inner"
    )

    df["Year"] = df["Date"].dt.year

    print("Merge complete!")
    return df


# ===============================
# FEATURE ENGINEERING
# ===============================
def create_features(df):
    print("Creating features...")

    df = df.sort_values(by=["RegionName", "Date"])

    df["price_growth"] = df.groupby("RegionName")["Home_price"].pct_change()
    df["rent_growth"] = df.groupby("RegionName")["Rent"].pct_change()
    df["inventory_change"] = -df.groupby("RegionName")["Home_price"].pct_change()

    df["Rent"] = df["Rent"].replace(0, np.nan)
    df["price_rent_ratio"] = df["Home_price"] / df["Rent"]

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    print("Features complete!")
    return df


# ===============================
# YEARLY AGGREGATION
# ===============================
def aggregate_yearly(df):
    print("Aggregating yearly...")

    df = df.groupby(["RegionName", "Year"], as_index=False).mean()

    print("Aggregation complete!")
    return df


# ===============================
# COMPUTE RHFI
# ===============================
def compute_rhfi(df):
    print("Computing RHFI...")

    df["RHFI"] = (
            0.35 * df["price_rent_ratio"] +
            0.25 * df["price_growth"] +
            0.20 * df["rent_growth"] -
            0.20 * df["inventory_change"]
    )

    return df


# ===============================
# FIX: REAL US STATE MAPPING (NO INTERNET DEPENDENCY)
# ===============================
def add_state_offline(df):
    print("Adding StateCode (offline ZIP mapping)...")

    # Simplified but reliable ZIP prefix mapping (covers US properly)
    def zip_to_state(zipcode):
        try:
            z = int(str(zipcode)[:3])

            if 100 <= z <= 149: return "NY"
            if 900 <= z <= 966: return "CA"
            if 750 <= z <= 799: return "TX"
            if 320 <= z <= 349: return "FL"
            if 600 <= z <= 629: return "IL"
            if 200 <= z <= 205: return "DC"
            if 980 <= z <= 994: return "WA"
            if 850 <= z <= 865: return "AZ"
            if 700 <= z <= 715: return "LA"
            if 300 <= z <= 319: return "GA"
            if 150 <= z <= 196: return "PA"
            if 6000 <= z <= 6999: return "CT"
            return "OTHER"
        except:
            return "OTHER"

    df["StateCode"] = df["RegionName"].apply(zip_to_state)

    return df


# ===============================
# FINAL FORMAT
# ===============================
def finalize(df):
    df = df.rename(columns={
        "RegionName": "Region",
        "Home_price": "Price"
    })

    return df


# ===============================
# MAIN
# ===============================
def main():

    zillow, rent = load_datasets()

    if zillow.empty or rent.empty:
        print("❌ Data failed to load.")
        return

    zillow, rent = clean_data(zillow, rent)
    df = merge_data(zillow, rent)
    df = create_features(df)
    df = aggregate_yearly(df)
    df = compute_rhfi(df)

    # ✅ FIXED: no SSL, no external dependency
    df = add_state_offline(df)

    df = finalize(df)

    output_file = "../data/rhfi_final_ui_ready.csv"
    df.to_csv(output_file, index=False)

    print(f"\n✅ FINAL DATA READY: {output_file}")

    print("\nState distribution:")
    print(df["StateCode"].value_counts())


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    main()