# Taking the csv files previously created and inserting all of that in the nft db

import sqlite3
import pandas as pd
import sys

# Read CSV files
nfts_df = pd.read_csv('nfts.csv')
nft_cids_df = pd.read_csv('nft_cids.csv')

# Merge the DataFrames on 'unique_key'
merged_df = pd.merge(nfts_df, nft_cids_df, on='unique_key')

# Connect to SQLite database
conn = sqlite3.connect('mathieu_nfts.db')
cursor = conn.cursor()

# Create the table
create_table_query = '''
CREATE TABLE IF NOT EXISTS mathieuNFTframe (
    identifier TEXT,
    collection TEXT,
    contract TEXT,
    token_standard TEXT,
    name TEXT,
    description TEXT,
    image_url TEXT,
    metadata_url TEXT,
    opensea_url TEXT,
    updated_at TEXT,
    is_disabled TEXT,
    is_nsfw TEXT,
    unique_key TEXT PRIMARY KEY,
    image_cid TEXT,
    metadata_cid TEXT,
    failed_base64_url TEXT
)
'''
cursor.execute(create_table_query)

# Prepare insert query with "INSERT OR IGNORE"
insert_query = '''
INSERT OR IGNORE INTO mathieuNFTframe (
    identifier, collection, contract, token_standard, name, description, image_url,
    metadata_url, opensea_url, updated_at, is_disabled, is_nsfw, unique_key,
    image_cid, metadata_cid, failed_base64_url
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# Insert data into the table row by row
for _, row in merged_df.iterrows():
    cursor.execute(insert_query, (
        row['identifier'], row['collection'], row['contract'], row['token_standard'],
        row['name'], row['description'], row['image_url'], row['metadata_url'],
        row['opensea_url_x'], row['updated_at'], row['is_disabled'], row['is_nsfw'],
        row['unique_key'], row['image_cid'], row['metadata_cid'], row['failed_base64_url']
    ))

# Commit the transaction
conn.commit()

# Fetch the first 5 rows and the total number of rows
cursor.execute('SELECT * FROM mathieuNFTframe LIMIT 5')
rows = cursor.fetchall()

cursor.execute('SELECT COUNT(*) FROM mathieuNFTframe')
total_rows = cursor.fetchone()[0]

# Print the frame header and the first 5 rows
print("Frame Header:", list(merged_df.columns))
print("First 5 Rows:")
for row in rows:
    print(row)

# Print the total number of rows
print("Total number of rows:", total_rows)

# Close the connection
conn.close()

sys.exit(0)
