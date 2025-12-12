import time
from datastream_direct.connection import connect
from datastream_direct.pandas_extras import fetch_frame

connection = connect(
    username="skrughoff+18@energydomain.com",
    password="p!Assword1",
    host="data-dev-api.energydomain.com",
    port=443,
    database="energy_domain",
)

cmd = """
SELECT foo FROM well_combined LIMIT 100
"""

cursor = connection.cursor()
t1 = time.time()
df = fetch_frame(cursor, cmd)
t2 = time.time()
print(df.head())
print(f"Time taken: {t2 - t1} seconds")

connection.close()
