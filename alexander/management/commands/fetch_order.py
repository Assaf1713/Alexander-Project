import requests 
from requests.auth import HTTPBasicAuth 

# WooCommerce API credentials
WOOCOMMERCE_API_URL = 'https://alexandertlv.com/wp-json/wc/v3/orders'
CONSUMER_KEY = 'ck_2fe9964a1d5c55d2b23d9300399421b4e6e93af6'
CONSUMER_SECRET = 'cs_7e1d5f9d6e2ce1a6af106f395885f70a94764c98'

# Fetch orders from WooCommerce API
response = requests.get(
    WOOCOMMERCE_API_URL,
    auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET)
)

if response.status_code == 200:
    # Print the response JSON (order data)
    orders_data = response.json()
    print(orders_data)
else:
    print(f"Failed to fetch orders: {response.status_code}")
