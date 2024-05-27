# pin it all to my ipfs node

import sqlite3
import requests
import threading
import sys

def pin_cid(client, cid):
    try:
        response = client.post(f"http://localhost:5001/api/v0/pin/add?arg={cid}&recursive=true")
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to pin CID {cid}: {e}")
        return False

def process_row(cursor, client, unique_key, image_cid, metadata_cid):
    print(f"Processing row with unique_key: {unique_key}, image_cid: {image_cid}, metadata_cid: {metadata_cid}")
    
    image_pinned_event = threading.Event()
    metadata_pinned_event = threading.Event()

    # Function to pin image CID
    def pin_image():
        nonlocal image_pinned_event
        image_pinned_event.set()
        return pin_cid(client, image_cid)

    # Function to pin metadata CID
    def pin_metadata():
        nonlocal metadata_pinned_event
        metadata_pinned_event.set()
        return pin_cid(client, metadata_cid) if metadata_cid else True

    # Start pinning threads
    image_thread = threading.Thread(target=pin_image)
    metadata_thread = threading.Thread(target=pin_metadata)

    image_thread.start()
    metadata_thread.start()

    # Wait for both threads to finish or timeout
    image_thread.join(timeout=60)
    metadata_thread.join(timeout=60)

    # Check if pinning completed successfully or timed out
    image_pinned = image_pinned_event.is_set()
    metadata_pinned = metadata_pinned_event.is_set()

    processed_pin = image_pinned and metadata_pinned if metadata_cid else image_pinned

    print(f"Image pinning successful: {image_pinned}")
    print(f"Metadata pinning successful: {metadata_pinned}")

    return processed_pin

def process_rows(cursor, client):
    cursor.execute("SELECT * FROM mathieuNFTframe")
    rows = cursor.fetchall()

    cursor.execute("PRAGMA table_info(mathieuNFTframe)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'processed_pin' not in columns:
        cursor.execute("ALTER TABLE mathieuNFTframe ADD COLUMN processed_pin BOOLEAN")

    for row in rows:
        unique_key = row[columns.index('unique_key')]
        image_cid = row[columns.index('image_cid')]
        metadata_cid = row[columns.index('metadata_cid')]

        if not image_cid:
            print(f"Skipping row with unique_key: {unique_key}, no image_cid provided")
            continue

        processed_pin = process_row(cursor, client, unique_key, image_cid, metadata_cid)

        cursor.execute("UPDATE mathieuNFTframe SET processed_pin = ? WHERE unique_key = ?", (processed_pin, unique_key))

    conn.commit()

def retry_failed_pins(cursor, client):
    cursor.execute("SELECT * FROM mathieuNFTframe WHERE processed_pin = FALSE")
    rows = cursor.fetchall()

    for row in rows:
        unique_key = row[columns.index('unique_key')]
        image_cid = row[columns.index('image_cid')]
        metadata_cid = row[columns.index('metadata_cid')]

        if not image_cid:
            print(f"Skipping retry pinning for row with unique_key: {unique_key}, no image_cid provided")
            continue

        processed_pin = process_row(cursor, client, unique_key, image_cid, metadata_cid)

        cursor.execute("UPDATE mathieuNFTframe SET processed_pin = ? WHERE unique_key = ?", (processed_pin, unique_key))

    conn.commit()

# Connect to SQLite database
conn = sqlite3.connect('mathieu_nfts.db')
cursor = conn.cursor()

# Process the rows and pin the CIDs
print("Processing rows...")
process_rows(cursor, requests)
print("Processing complete.")

# Retry failed pins
print("Retrying failed pins...")
retry_failed_pins(cursor, requests)
print("Retry complete.")

# Fetch the first 5 rows and print them
cursor.execute("SELECT * FROM mathieuNFTframe LIMIT 5")
rows = cursor.fetchall()

# Print the frame header and the first 5 rows
cursor.execute("PRAGMA table_info(mathieuNFTframe)")
columns = [col[1] for col in cursor.fetchall()]
print("Frame Header:", columns)
print("First 5 Rows:")
for row in rows:
    print(row)

# Close the database connection
conn.close()
print("Pinning process completed. Exiting...")
exit(0)
sys.exit(0)
