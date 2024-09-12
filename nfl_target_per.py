import requests
from bs4 import BeautifulSoup
import re

def scrape_target_percentage(url, position):
    # Make the request to the page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with id 'data'
    table = soup.find('table', {'id': 'data'})
    player_data = []

    if table:
        headers = [th.get_text(strip=True) for th in table.find_all('th')]

        # Find the index of 'TM %' column
        tm_percentage_index = headers.index("% TM")

        # Iterate through rows and extract data for 'TM %' column
        for row in table.find_all('tr')[1:]:  # Skip header row
            columns = row.find_all('td')
            if columns:
                player = columns[1].get_text(strip=True)
                cleaned_player = re.sub(r'\(.*?\)', '', player).strip()  # Clean player name
                tm_percentage = columns[tm_percentage_index].get_text(strip=True)
                player_data.append({
                    "Player": cleaned_player,
                    "Position": position,
                    "TG %": tm_percentage
                })
    else:
        print(f"Table not found for {position}")

    return player_data

def combine_wr_te_target_data():
    # URLs for WR and TE
    wr_url = "https://www.fantasypros.com/nfl/advanced-stats-wr.php?year=2023"
    te_url = "https://www.fantasypros.com/nfl/advanced-stats-te.php?year=2023"

    # Scrape WR and TE data
    wr_data = scrape_target_percentage(wr_url, "WR")
    te_data = scrape_target_percentage(te_url, "TE")

    # Combine both WR and TE data into a single list
    combined_data = wr_data + te_data

    # Print the combined data
    for player_info in combined_data:
        print(f"Player: {player_info['Player']}, Position: {player_info['Position']}, TM %: {player_info['TM %']}")

    return combined_data

# Call the function to get the combined data
combined_data = combine_wr_te_target_data()
