import mariadb
import phpserialize
import json
from dotenv import load_dotenv
import os
import http.client

# Get the current informal rates
conn = http.client.HTTPSConnection("exchange-rate.decubba.com")
payload = ''
headers = {
    'User-Agent': 'Apidog/1.0.0 (https://apidog.com)'
}
conn.request("GET", "/api/informal/cup", payload, headers)
res = conn.getresponse()
data = res.read()
data_array = json.loads(data)

# Rates using dollar as base
cup_rate = float(data_array['exchange_rate'][0]["mid"])
mlc_rate = cup_rate/float(data_array['exchange_rate'][1]["mid"])
eur_rate = cup_rate/float(data_array['exchange_rate'][2]["mid"])
print(f'cup_rate: {cup_rate}')
print(f'mlc_rate: {mlc_rate}')
print(f'eur_rate: {eur_rate}')

# Get secrets
load_dotenv()
username = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_URL')
port = int(os.getenv('DB_PORT'))
database = os.getenv('DATABASE')
prefix = os.getenv('TABLE_PREFIX')

# Connect to the database
conn = mariadb.connect(
    user=username,
    password=password,
    host=host,
    port=port,
    database=database

)


# Get the current value of the "rate_custom" column
cur = conn.cursor()
cur.execute(
    f"SELECT option_value FROM {prefix}_options WHERE option_name='wcu_currencies'")
row = cur.fetchone()
option_value = row[0]

# Parse the option_value as a dictionary
php_array = phpserialize.loads(option_value.encode('utf-8'))
print(php_array)
# exit(0)

php_array = phpserialize.loads(option_value.encode('utf-8'))
php_array[b'COP'][b'rate_custom'] = cup_rate
php_array[b'EUR'][b'rate_custom'] = eur_rate
php_array[b'MDL'][b'rate_custom'] = mlc_rate
new_option_value = phpserialize.dumps(php_array)

# Update the value in the database
cur.execute(
    f"UPDATE {prefix}_options SET option_value=%s WHERE option_name='wcu_currencies'", (new_option_value,))

# Commit the changes to the database
conn.commit()

# Close the connection to the database
cur.close()
conn.close()
