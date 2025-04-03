import pandas as pd
from datetime import datetime, timedelta
 
# Define the URL for the exchange rates
url =  "https://www.xe.com/currencytables/?from=EUR&to=CNY&date={}"
 
 
# Define the date range
start_date = datetime(2021, 1, 1)
end_date = datetime.today() - timedelta(days=1)
 
# Create an empty list to store the exchange rates
exchange_rates = []
 
# Loop through each date in the range
for single_date in pd.date_range(start_date, end_date):
    # Format the date as YYYY-MM-DD
    date_str = single_date.strftime("%Y-%m-%d")
   
    # Construct the URL for the exchange rates
    url_date = url.format(date_str)
   
    try:
        # Read the HTML table from the website
        tables = pd.read_html(url_date)
       
        # Get the exchange rates table
        exchange_rates_table = tables[0]
       
        # Add the date to the exchange rates table
        exchange_rates_table['Date'] = date_str
       
        # Append the exchange rates table to the list
        exchange_rates.append(exchange_rates_table)
       
    except Exception as e:
        print(f"Error occurred on {date_str}: {str(e)}")
 
# Concatenate the exchange rates tables
if exchange_rates:
    exchange_rates_df = pd.concat(exchange_rates, ignore_index=True)
    print("Exchange rates data collected successfully.")
else:
    print("No exchange rates data collected.")
 
exchange_rates_df['Date'] = pd.to_datetime(exchange_rates_df['Date'])
exchange_rates_df = pd.DataFrame(exchange_rates_df)
exchange_rates_df = exchange_rates_df.reset_index(drop=True)
# Define the currencies of interest
currencies_of_interest = ['CZK', 'USD', 'PLN', 'RON', 'HUF', 'TRY', 'AUD', 'MXN', 'GBP',
                          'BAM', 'MAD', 'TND', 'EUR', 'RSD', 'SGD', 'CHF', 'DKK', 'INR',
                          'NOK', 'BGN', 'KRW', 'TWD', 'JPY', 'CAD', 'CNY', 'THB', 'VND']
# Filter the dataframe
forex_rates_ = exchange_rates_df[exchange_rates_df.iloc[:, 0].isin(currencies_of_interest)].copy()
forex_rates_['InvoiceDate'] = pd.to_datetime(forex_rates_['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
forex_rates_.InvoiceDate.dtype