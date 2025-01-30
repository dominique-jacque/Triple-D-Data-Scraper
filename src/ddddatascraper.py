import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import boto3

# List of states for the trial run
trial_states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# Base URL for each state's page
base_url = 'https://www.dinersdriveinsdives.com/loc/{}/'

# Function to scrape data for a single state, handling pagination
def scrape_state_data(state):
    page_number = 1
    diners = []

    while True:
        url = base_url.format(state) if page_number == 1 else base_url.format(state) + f'{page_number}/'
        print(f"Scraping {state}, Page {page_number}...")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to retrieve data for {state}, Page {page_number}. Skipping...")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select('tr[id^="check_"]')

        if not rows:
            print(f"No more results found for {state}, stopping at Page {page_number}.")
            break

        for row in rows:
            try:
                name_tag = row.find('div', class_='media-body').find('a')
                name = name_tag.text.strip() if name_tag else 'N/A'

                address_tag = row.find('div', class_='media-body')
                if address_tag:
                    address_parts = address_tag.decode_contents().split('<br>')
                    street_address = BeautifulSoup(address_parts[0], 'html.parser').text.strip() if len(address_parts) > 0 else 'N/A'
                    city_state_zip = BeautifulSoup(address_parts[1], 'html.parser').text.strip() if len(address_parts) > 1 else 'N/A'
                    phone = BeautifulSoup(address_parts[2], 'html.parser').text.strip() if len(address_parts) > 2 else 'N/A'
                    city, state_zip = city_state_zip.split(',') if ',' in city_state_zip else ('N/A', 'N/A')
                    address = f"{street_address}, {city.strip()}, {state_zip.strip()}"
                else:
                    address, phone = 'N/A', 'N/A'

                website_tag = row.find('a', text=True)
                website = website_tag['href'] if website_tag else 'N/A'

                episode_info_tag = row.find('div', class_='d-xs-block d-sm-none')
                episode_info = episode_info_tag.get_text(separator="\n").strip() if episode_info_tag else 'N/A'

                diners.append({
                    'State': state,
                    'Name': name,
                    'Address': address,
                    'Phone': phone,
                    'Website': website,
                    'Episode Info': episode_info
                })
            except AttributeError:
                print(f"Error extracting data for a row in {state}. Skipping...")

        page_number += 1

    return diners

# Scrape all states in parallel
all_diners = []
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(scrape_state_data, trial_states)

for result in results:
    all_diners.extend(result)

# Convert the list to a DataFrame
df = pd.DataFrame(all_diners)

# Save data if DataFrame is not empty
csv_file = 'ddddata-allstates.csv'
if not df.empty:
    df_sorted = df.sort_values(by='State')
    df_sorted.to_csv(csv_file, index=False)
    print(f"Diner data for trial states saved to {csv_file}")
else:
    print("No data found to save.")

# Function to upload CSV file to S3
def upload_csv_to_s3(file_name, bucket_name, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
        print(f"File '{file_name}' uploaded to '{bucket_name}/{object_name}'.")
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

# Upload to S3
bucket_name = 'dddscrapeddata'
if df.empty:
    print("Skipping upload, no data to save.")
else:
    upload_csv_to_s3(csv_file, bucket_name)
