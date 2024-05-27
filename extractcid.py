## extracting CIDs from nfts.csv 

import csv
import re
import base64
import binascii
from urllib.parse import urlparse, unquote
import sys


def extract_ipfs_cid(url, opensea_url):
    # Check if the URL contains "/ipfs/"
    if "/ipfs/" in url:
        ipfs_cid = url.split("/ipfs/")[1].split("/")[0]
        return ipfs_cid, None

    # Check if the URL starts with "ipfs://"
    if url.startswith("ipfs://"):
        ipfs_cid = url.split("ipfs://")[1].split("/")[0]
        return ipfs_cid, None

    # Check if the URL is a base64-encoded JSON
    if url.startswith("data:application/json;base64,"):
        encoded_json = url.split(",")[1]

        try:
            # Try to decode the base64 string
            decoded_json = base64.b64decode(encoded_json).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            # If the decoding fails, return the failed base64 URL
            return None, url

        # Use regular expression to extract the IPFS CID
        ipfs_cid_match = re.search(r'"ipfs://(.+?)"', decoded_json)
        if ipfs_cid_match:
            ipfs_cid = ipfs_cid_match.group(1)
            return ipfs_cid, None

        ipfs_cid_match = re.search(r'"/ipfs/(.+?)"', decoded_json)
        if ipfs_cid_match:
            ipfs_cid = ipfs_cid_match.group(1)
            return ipfs_cid, None

    return None, None

with open("nfts.csv", "r", encoding="utf-8") as csvfile, open("nft_cids.csv", "w", newline='', encoding="utf-8") as output_file:
    reader = csv.DictReader(csvfile)
    fieldnames = ["image_cid", "metadata_cid", "failed_base64_url", "opensea_url", "unique_key"]
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        image_url = row["image_url"]
        metadata_url = row["metadata_url"]
        opensea_url = row["opensea_url"]
        unique_key = row["unique_key"]
        image_ipfs_cid, _ = extract_ipfs_cid(image_url, None)
        metadata_ipfs_cid, failed_base64_url = extract_ipfs_cid(metadata_url, opensea_url)
        if image_ipfs_cid:
            image_ipfs_cid = image_ipfs_cid.split(",")[0].strip()
        if metadata_ipfs_cid:
            metadata_ipfs_cid = metadata_ipfs_cid.split(",")[0].strip()
        writer.writerow({
            "image_cid": image_ipfs_cid,
            "metadata_cid": metadata_ipfs_cid,
            "failed_base64_url": failed_base64_url,
            "opensea_url": opensea_url,
            "unique_key": unique_key
        })

sys.exit(0)
