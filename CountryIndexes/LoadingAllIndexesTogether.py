import pandas as pd
from pathlib import Path

# Define file path
cleaned_data_file = Path("CountryIndexes/cleaned_data.csv")

# Read the cleaned data
df_cleaned = pd.read_csv(cleaned_data_file)

# Drop the 'ISO-3 Code' column if it exists
df_cleaned = df_cleaned.drop(columns=["ISO-3 Code"], errors="ignore")

# Convert latest_value to numeric, forcing errors to NaN
df_cleaned["latest_value"] = pd.to_numeric(df_cleaned["latest_value"], errors="coerce")

# Remove rows where latest_value is NaN (i.e., missing or non-numeric)
df_cleaned = df_cleaned.dropna(subset=["latest_value"]).copy()

# Save the cleaned data
df_cleaned.to_csv(cleaned_data_file, index=False)

print(f"Final cleaned data saved to {cleaned_data_file}")
