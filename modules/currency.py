import requests

# A mapping for the most common currencies
unicode_to_currency = {
    '€': 'EUR',   # Euro
    '$': 'USD',   # US Dollar
    '£': 'GBP',   # British Pound
}

conversion_rates = {}

# This variable is used to check if the currrency have been retrieved from the API
# This is used to call the API only the first time that the function convert_to_EUR is called
# In this way we can save time and resources (since the API has a limit of 1500 requests per month)
already_loaded = False

def retrive_conversion_rates():
    """
    This function retrieves the conversion rates from the site exchangerate-api.com
    and stores them in a global variable
    In case of API not available or error in the request, it raises an exception
    """
    # The following url can be used to get the latest exchange rate data for EUR
    url = "https://v6.exchangerate-api.com/v6/fdf5a4c8c24fea3b32a629ef/latest/"+ "EUR"

    try:
        # The result of the request is stored in a dictionary because the result is in JSON format
        result = requests.get(url).json()
        if result["result"] == "error":
            # In case of an error in the request we raise an exception
            print("Error: "+result["error-type"])

        global conversion_rates 
        conversion_rates = result["conversion_rates"]
        
    except Exception as e:
        print(e)

# The following function converts a given amount of money from one currency to EUR
def convert_to_EUR(amount: float, currency: str) -> float:
    """
    This function converts a given amount of money from one currency to EUR
    Args:
        amount (float): The amount of money to convert
        currency (string): The currency of the amount
    Returns:
        float: The converted amount (None if not able to convert)
    """
    # The following variable is used to check if the currrency have been retrieved from the API
    # This is used to call the API only the first time that the function convert_to_EUR is called
    global already_loaded
    if not already_loaded:
        retrive_conversion_rates()
        already_loaded = True
    # Get currency code from unicode symbol
    currency = unicode_to_currency.get(currency, 'Unknown')

    # Convert the currency (if possible)
    if currency in conversion_rates:
        return amount/conversion_rates[currency]
    else:
        return None


