import requests
import matplotlib.pyplot as plt
import numpy as np


# EIA API key and URL
API_KEY = "olNnH6iSyPabk6zGefAKF6J3B5VW30dCmCMSr1Wh"
API_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

# Parameters for the API request
params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": "value",
    "facets[product][]": "EPMR",
    "facets[duoarea][0]": "Y05SF",  # Los Angeles
    "start": "2010",  # Start year for the range (change this as needed)
    "end": "2026",    # End year for the range (change this as needed)
}

try:
    # Send the GET request
    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Check if data exists
    monthly_prices = data.get("response", {}).get("data", [])

    if monthly_prices:
        # Manually sort the list of prices by period (date)
        sorted_prices = []
        for entry in monthly_prices:
            inserted = False
            period = entry["period"]
            for i in range(len(sorted_prices)):
                if period < sorted_prices[i]["period"]:
                    sorted_prices.insert(i, entry)
                    inserted = True
                    break
            if not inserted:
                sorted_prices.append(entry)

        print("\nMonthly California Regular Gasoline Prices (Sorted by Date):")
        for entry in sorted_prices:
            date = entry.get("period", "Unknown date")
            price = entry.get("value")
            print(f"Date: {date}, Price: ${float(price):.2f} per gallon" if price else f"Date: {date}, Price: Data unavailable")
    else:
        print("\nNo data found in the API response.")

except requests.exceptions.RequestException as e:
    print(f"\nError fetching data from EIA API: {e}")
except KeyError as e:
    print(f"\nError parsing response: Missing key {e}")


storedPrices = []
storedYears = []
i =0
for i in range(180):
    storedPrices.append((float(sorted_prices[i]["value"])))
    storedYears.append((sorted_prices[i]["period"][0:7]))
#print(storedYears)
#print(storedPrices)


i = 0
for year in range(2010,2025):
    dateArray = []
    priceArray = []
    while i <= 11:
        dateArray.append((sorted_prices[i + (year-2010)*12]["period"][5:7]))
        priceArray.append((float(sorted_prices[i + (year-2010)*12]["value"])))
        i += 1
    
    plt.xlabel('Dates')
    plt.ylabel('Prices (Per Gallon)')
    plt.title(f'Current Gas Prices in California (Year {year})')
    plt.plot(dateArray, priceArray)
    plt.show()
    dateArray = []
    priceArray = []
    i=0




