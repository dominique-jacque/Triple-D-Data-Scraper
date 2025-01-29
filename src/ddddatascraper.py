import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

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
        # Construct the URL based on the page number
        if page_number == 1:
            url = base_url.format(state)
        else:
            url = base_url.format(state) + f'{page_number}/'

        print(f"Scraping {state}, Page {page_number}...")  # Log progress
        response = requests.get(url)

        # Check for valid response
        if response.status_code != 200:
            print(f"Failed to retrieve data for {state}, Page {page_number}. Skipping...")
            break

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the <tr> elements where id starts with "check_"
        rows = soup.select('tr[id^="check_"]')

        # If no rows are found, break the loop (no more pages)
        if not rows:
            print(f"No more results found for {state}, stopping at Page {page_number}.")
            break

        for row in rows:
            try:
                # Extract diner name
                name_tag = row.find('div', class_='media-body').find('a')
                name = name_tag.text.strip() if name_tag else 'N/A'

                # Extract address details
                address_tag = row.find('div', class_='media-body')
                if address_tag:
                    # Split based on <br> tags for address details
                    address_parts = address_tag.decode_contents().split('<br>')
                    street_address = BeautifulSoup(address_parts[0], 'html.parser').text.strip() if len(address_parts) > 0 else 'N/A'
                    city_state_zip = BeautifulSoup(address_parts[1], 'html.parser').text.strip() if len(address_parts) > 1 else 'N/A'
                    phone = BeautifulSoup(address_parts[2], 'html.parser').text.strip() if len(address_parts) > 2 else 'N/A'

                    # Split city, state, and zip code if available
                    if city_state_zip != 'N/A' and ',' in city_state_zip:
                        city_state = city_state_zip.split(',')
                        city = city_state[0].strip() if len(city_state) > 0 else 'N/A'
                        state_zip = city_state[1].strip() if len(city_state) > 1 else 'N/A'
                    else:
                        city = 'N/A'
                        state_zip = 'N/A'
                    
                    address = f"{street_address}, {city}, {state_zip}"
                else:
                    address = 'N/A'
                    phone = 'N/A'

                # Extract website
                website_tag = row.find('a', text=True)
                website = website_tag['href'] if website_tag else 'N/A'

                # Extract episode information
                episode_info_tag = row.find('div', class_='d-xs-block d-sm-none')
                episode_info = episode_info_tag.get_text(separator="\n").strip() if episode_info_tag else 'N/A'

                # Append the extracted data to the diners list
                diners.append({
                    'State': state,  # Add the state abbreviation
                    'Name': name,
                    'Address': address,
                    'Phone': phone,
                    'Website': website,
                    'Episode Info': episode_info
                })

            except AttributeError:
                print(f"Error extracting data for a row in {state}. Skipping...")

        # Move to the next page
        page_number += 1

    return diners

# Scrape all states in parallel
all_diners = []

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(scrape_state_data, trial_states)

# Combine results from all states
for result in results:
    all_diners.extend(result)

# Convert the list to a DataFrame
df = pd.DataFrame(all_diners)

# Check if DataFrame has data before sorting
if not df.empty:
    # Sort the data by State alphabetically
    df_sorted = df.sort_values(by='State')
    
    # Save the data to a CSV file
    df_sorted.to_csv('diners_trial_states_full.csv', index=False)
    print("Diner data for trial states has been saved to diners_trial_states_full.csv")
else:
    print("No data found to save.")
