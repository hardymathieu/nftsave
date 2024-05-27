# download the image based on the links returned by Opensea

import os
import requests
import sqlite3
from urllib.parse import urlparse
import sys



# Define the directory to save images
output_dir = 'db_downloaded_images'


def download_image(url, save_path):

    try:

        response = requests.get(url, stream=True)

        response.raise_for_status()

        

        # Ensure that the save path is not a directory

        if os.path.isdir(save_path):

            print(f"Path {save_path} is a directory.")

            return False



        with open(save_path, 'wb') as file:

            for chunk in response.iter_content(1024):

                file.write(chunk)

        

        return True

    except requests.exceptions.RequestException as e:

        print(f"Failed to download {url}: {e}")

        return False

    except Exception as e:

        print(f"An unexpected error occurred while downloading {url}: {e}")

        return False



def generate_unique_filename(url):

    parsed_url = urlparse(url)

    filename = os.path.basename(parsed_url.path)

    

    # Add a check to handle cases where the filename might be empty

    if not filename:

        filename = url.split('/')[-1] or 'downloaded_file'

        

    return filename



# Connect to SQLite database

conn = sqlite3.connect('mathieu_nfts.db')

cursor = conn.cursor()



# Check if img_downloaded column exists, and add it if it doesn't

cursor.execute("PRAGMA table_info(mathieuNFTframe)")

columns = [col[1] for col in cursor.fetchall()]

if 'img_downloaded' not in columns:

    cursor.execute("ALTER TABLE mathieuNFTframe ADD COLUMN img_downloaded TEXT")

    conn.commit()



# Fetch rows where img_downloaded is NULL or FAIL

cursor.execute("SELECT collection, image_url, unique_key FROM mathieuNFTframe WHERE img_downloaded IS NULL OR img_downloaded = 'FAIL'")

rows = cursor.fetchall()



# Ensure the output directory exists

os.makedirs(output_dir, exist_ok=True)



for row in rows:

    collection, image_url, unique_key = row

    success = True



    if not image_url:

        print(f"No URL found for entry with unique_key {unique_key}.")

        success = False

    else:

        # Create a subdirectory for the collection if it doesn't exist

        collection_dir = os.path.join(output_dir, collection)

        os.makedirs(collection_dir, exist_ok=True)



        # Generate a unique filename for the image based on its URL

        image_filename = generate_unique_filename(image_url)

        image_save_path = os.path.join(collection_dir, image_filename)



        # Download image from image_url

        if image_url:

            if not download_image(image_url, image_save_path):

                success = False



    # Update the img_downloaded field in the database

    img_downloaded_status = 'TRUE' if success else 'FAIL'

    try:

        cursor.execute("UPDATE mathieuNFTframe SET img_downloaded = ? WHERE unique_key = ?", (img_downloaded_status, unique_key))

        conn.commit()

    except sqlite3.DatabaseError as e:

        print(f"Failed to update database for unique_key {unique_key}: {e}")

        success = False



# Close the database connection

conn.close()

# Exit the script gracefully

print("Pinning process completed. Exiting...")

sys.exit(0)

