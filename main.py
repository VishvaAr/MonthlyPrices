import requests

# EIA API key and URL
API_KEY = "olNnH6iSyPabk6zGefAKF6J3B5VW30dCmCMSr1Wh"
API_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

# Parameters for the API request
params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": "value",
    "facets[product][]": "EPMR",
    "facets[duoarea][0]": "Y05LA",  # Los Angeles
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