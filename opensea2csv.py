## getting OPENSEA data to CSV & text file for posterity
## this outputs
## - a File os-save-timestap.txt  > should have the logs, but is always empty -- I'll figure it out later :) 
## - a file nfts.csv (which will be overridden whenever the script runs)
## - a file all_nfts_timestamp > contains all NFTs found during this run
## It creates a "unique_id" so that it's easy to join other tables
## check line 29 for your opensea api key
## check line 50 for the blockchains you want to look at
## check line 90 for the addresses you want to monitor

# Set up logging
current_time = datetime.now()
log_filename = f"os-save-nft-{current_time.minute}-{current_time.hour}-{current_time.day}-{current_time.month}-{current_time.year}.txt"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable the default console handler
root_logger = logging.getLogger()
root_logger.handlers.clear()

file_handler = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

def fetch_nfts(chain, account_address, cursor=None):
    base_url = f"https://api.opensea.io/api/v2/chain/{chain}/account/{account_address}/nfts"
    headers = {
        "accept": "application/json",
        "x-api-key": "YOUR_OPENSEA_API_KEY" #you'll find more info here https://docs.opensea.io/
    }
    params = {
        "limit": 199
    }
    if cursor:
        params['next'] = cursor

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        logging.info(f"API Response Code: {response.status_code}")
        logging.info(f"API Response: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching NFTs: {e}")
        return None

def fetch_all_nfts(account_addresses):
    all_nfts = []
    chains = ["base", "ethereum", "matic","optimism","zora"] #add any chains that OpenSea supports
    for account_address in account_addresses:
        for chain in chains:
            cursor = None
            while True:
                nfts_data = fetch_nfts(chain, account_address, cursor)
                if nfts_data and 'nfts' in nfts_data:
                    all_nfts.extend(nfts_data['nfts'])
                if nfts_data and 'next' in nfts_data and nfts_data['next'] is not None:
                    cursor = nfts_data['next']
                else:
                    break  # Exit loop if there are no more pages

                # Retry mechanism
                if nfts_data is None:
                    logging.info("Retrying after 5 seconds...")
                    time.sleep(5)
                    continue

    # Write all_nfts to a .txt file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"all_nfts_{timestamp}.txt"
    with open(output_filename, "w") as f:
        for nft in all_nfts:
            f.write(str(nft) + "\n")

    return all_nfts

def save_nfts_to_csv(nfts, filename='nfts.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(nfts[0].keys()) + ['unique_key']  # Add 'unique_key' to the fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nft in nfts:
            identifier = nft.get('identifier')
            contract = nft.get('contract')
            unique_key = f"cntrct:{contract}withid:{identifier}"  # Create the unique_key string
            nft['unique_key'] = unique_key  # Add the unique_key to the dictionary
            writer.writerow(nft)

account_addresses = [
    "0x....blockchain address 1",
    "0x....blockchain address 2"
]

try:
    all_nfts = fetch_all_nfts(account_addresses)
    logging.info(f"Total NFTs fetched: {len(all_nfts)}")
    save_nfts_to_csv(all_nfts, 'nfts.csv')
except Exception as e:
    logging.error(f"An error occurred: {e}")

sys.exit(0)
