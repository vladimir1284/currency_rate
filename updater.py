import mariadb
import phpserialize
import json
from dotenv import load_dotenv
import os

new_value = 200

# Get secrets
load_dotenv()
username = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_URL')
port = os.getenv('DB_PORT')
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
php_array[b'CUP'][b'rate_custom'] = new_value
new_option_value = phpserialize.dumps(php_array)

# Update the value in the database
cur.execute(
    f"UPDATE {prefix}_options SET option_value=%s WHERE option_name='wcu_currencies'", (new_option_value,))

# Commit the changes to the database
conn.commit()

# Close the connection to the database
cur.close()
conn.close()
