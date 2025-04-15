import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

# Load state tax data
years_numeric = list(range(2015, 2025))  # Numeric year values for regression
state_taxes_values = []
state_numbers = [11, 12, 16, 28, 30, 39, 42, 50, 54]
years_labels = ['January 2025', 'January 2024', 'January 2023', 'January 2022', 'January 2021_revised', 
                'January 2020', 'January 2019 ', 'January 2018', 'January 2017', 'January 2016', 'January 2015']

for i in range(9):
    state_taxes_per_state = []

    for j in range(10, 0, -1):
        df = pd.read_excel('fueltaxes.xlsx', sheet_name=years_labels[j])
        state_taxes = df.loc[state_numbers[i]]["Unnamed: 1"]
        state_taxes_per_state.append(state_taxes)

    state_taxes_values.append(state_taxes_per_state)

# Plot state taxes & linear regression
plt.figure(figsize=(12, 7))

for i in range(9):
    plt.plot(years_numeric, state_taxes_values[i], marker='o', label=f"State {state_numbers[i]}")

    # Linear regression
    coef = np.polyfit(years_numeric, state_taxes_values[i], 1)
    trendline = np.polyval(coef, years_numeric)
    plt.plot(years_numeric, trendline, linestyle="--", alpha=0.7)

plt.xlabel('Year')
plt.ylabel('State Taxes (USD per gallon)')
plt.title('State Taxes Over Time (2015-2025)')
plt.xticks(years_numeric, rotation=45)
plt.grid(True)
plt.legend()
plt.show()

# Residual plot for state taxes
plt.figure(figsize=(12, 5))

for i in range(9):
    predicted = np.polyval(np.polyfit(years_numeric, state_taxes_values[i], 1), years_numeric)
    residuals = np.array(state_taxes_values[i]) - predicted
    plt.scatter(years_numeric, residuals, label=f"State {state_numbers[i]}")

plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel('Year')
plt.ylabel('Residuals')
plt.title('Residuals for State Taxes Regression')
plt.legend()
plt.grid(True)
plt.show()

# --- Fetch gas prices from EIA API --- move key to a secrets json file
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

locations = {
    "SCA": "California",
    "SCO": "Colorado",
    "SFL": "Florida",
    "SNY": "New York",
    "STX": "Texas"
}

params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": "value",
    "start": "2010",
    "end": "2026",
}

all_data = {}

try:
    for location, name in locations.items():
        params["facets[duoarea][0]"] = location
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        monthly_prices = data.get("response", {}).get("data", [])

        if monthly_prices:
            sorted_prices = sorted(monthly_prices, key=lambda x: x["period"])
            all_data[name] = sorted_prices
        else:
            print(f"No data found for {name}.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    exit()

yearly_data = {name: {} for name in locations.values()}

for location_name, sorted_prices in all_data.items():
    for entry in sorted_prices:
        year = int(entry["period"][:4])
        price = entry["value"]

        if price is None:
            continue

        price = float(price)
        if year not in yearly_data[location_name]:
            yearly_data[location_name][year] = []
        yearly_data[location_name][year].append(price)

for location_name, yearly_prices in yearly_data.items():
    for year, prices in yearly_prices.items():
        yearly_data[location_name][year] = sum(prices) / len(prices)

# Plot gas prices & linear regression
plt.figure(figsize=(12, 7))

for location_name, yearly_prices in yearly_data.items():
    years = sorted(yearly_prices.keys())
    averages = [yearly_prices[year] for year in years]

    plt.plot(years, averages, marker='o', label=location_name)

    # Linear regression
    coef = np.polyfit(years, averages, 1)
    trendline = np.polyval(coef, years)
    plt.plot(years, trendline, linestyle="--", alpha=0.7)

plt.xlabel('Year')
plt.ylabel('Average Price (USD per gallon)')
plt.title('Average Gasoline Prices Comparison (2010-2025)')
plt.grid(True)
plt.legend()
plt.show()

# Residual plot for gas prices
plt.figure(figsize=(12, 5))

for location_name, yearly_prices in yearly_data.items():
    years = sorted(yearly_prices.keys())
    averages = [yearly_prices[year] for year in years]

    predicted = np.polyval(np.polyfit(years, averages, 1), years)
    residuals = np.array(averages) - predicted
    plt.scatter(years, residuals, label=location_name)

plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel('Year')
plt.ylabel('Residuals')
plt.title('Residuals for Gas Prices Regression')
plt.legend()
plt.grid(True)
plt.show()
