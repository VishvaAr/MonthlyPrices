import requests
import matplotlib.pyplot as plt
import numpy as np

# EIA API key and URL
API_KEY = "olNnH6iSyPabk6zGefAKF6J3B5VW30dCmCMSr1Wh"
API_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

# Parameters for the API request
locations = {
    #"Y05LA": "Los Angeles",
    #"Y05SF": "San Francisco",
    "SCA": "Southern California",
}

params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": "value",
    "start": "2010",  # Start year for the range
    "end": "2026",    # End year for the range
}

# Store data for each location
all_data = {}

try:
    for location, name in locations.items():
        # Set the location-specific facet
        params["facets[duoarea][0]"] = location

        # Send the GET request
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract and sort data by date
        monthly_prices = data.get("response", {}).get("data", [])
        if monthly_prices:
            sorted_prices = sorted(monthly_prices, key=lambda x: x["period"])
            all_data[name] = sorted_prices
        else:
            print(f"\nNo data found for {name}.")

except requests.exceptions.RequestException as e:
    print(f"\nError fetching data from EIA API: {e}")
    exit()
except KeyError as e:
    print(f"\nError parsing response: Missing key {e}")
    exit()

# Calculate yearly average prices and prepare for plotting
yearly_data = {name: {} for name in locations.values()}

for location_name, sorted_prices in all_data.items():
    for entry in sorted_prices:
        year = entry["period"][:4]  # Extract year
        price = entry["value"]      # Get the price value
        print(f'Year: {year}, Price: {price}')
        # Skip entries where price is None
        if price is None:
            continue

        price = float(price)  # Convert to float after checking for None

        if year not in yearly_data[location_name]:
            yearly_data[location_name][year] = []
        yearly_data[location_name][year].append(price)

# Calculate yearly averages
for location_name, yearly_prices in yearly_data.items():
    for year, prices in yearly_prices.items():
        yearly_data[location_name][year] = sum(prices) / len(prices)

# Plot yearly average prices for all locations
plt.figure(figsize=(12, 7))
for location_name, yearly_prices in yearly_data.items():
    years = sorted(yearly_prices.keys())
    averages = [yearly_prices[year] for year in years]
    plt.plot(years, averages, marker='o', label=location_name)

plt.xlabel('Year')
plt.ylabel('Average Price (USD per gallon)')
plt.title('Average Gasoline Prices Comparison (2010-2025)')
plt.legend()
plt.grid(True)
plt.show()


S0 = 4.19  # Latest price (e.g., January 2025)
mu = 0.014  # Drift (monthly return)
sigma = 0.31  # Volatility (monthly volatility)
T = 1  # Time horizon in years
dt = 1/12  # Time step (monthly)
steps = int(T / dt)  # Number of time steps
n_simulations = 10  # Number of simulations

# Simulate GBM
np.random.seed(42)  # For reproducibility

# Simulate the GBM process for multiple paths
simulated_prices = np.zeros((n_simulations, steps))
for i in range(n_simulations):
    # Generate random walk (Wiener process) increments
    dW = np.random.normal(0, np.sqrt(dt), steps)
    # Calculate the path using the GBM formula
    price_path = S0 * np.exp(np.cumsum((mu - 0.5 * sigma**2) * dt + sigma * dW))
    simulated_prices[i] = price_path

# Plot the simulated paths
plt.figure(figsize=(10, 6))
for i in range(n_simulations):
    plt.plot(simulated_prices[i], label=f"Simulation {i+1}")
plt.title("Geometric Brownian Motion Simulations")
plt.xlabel("Time (Months)")
plt.ylabel("Simulated Price")
plt.legend()
plt.grid(True)
plt.show()
