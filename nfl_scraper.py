import requests 
import pickle
from bs4 import BeautifulSoup as bs

from selenium import webdriver
import time

url = "https://www.nfl.com/stats/player-stats/"
url2 = "https://www.pro-football-reference.com/years/2023/opp.htm"

def scrape_page2(url2):

    driver = webdriver.Safari()

    driver.get(url2)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')

    table = soup.find('table', {'id': 'team_stats'})
    if not table: 
        print("table not found")
        return 
    
    header_row = table.find('tr', class_=lambda x: x != 'over_header')

    # Extract the headers from that 'tr'
    headers = [th.getText().strip() for th in header_row.find_all('th')]

    plays_index = headers.index("Ply")
    games_index = headers.index("G")
    passes_index = headers.index("Att")

    att_indices = [i for i, header in enumerate(headers) if header == "Att"]
    if len(att_indices) > 1:
        rushes_index = att_indices[1]

    rows = table.find_all('tr')[2:]  # Skip the first two rows (over-headers and actual headers)
    plays_stats = []

    for row in rows[:-3]:
        columns = row.find_all('td')
        if columns:
            team_name = columns[0].getText().strip()
            games_played = columns[games_index-1].getText().strip()
            plays = columns[plays_index-1].getText().strip()
            passes = columns[passes_index-1].getText().strip()
            rushes = columns[rushes_index -1].getText().strip()
           
            games_played_int = int(games_played)
            passes_int = int(passes)
            rushes_int = int(rushes)

            plays_int = float(plays)

            plays_per_game = round(plays_int / games_played_int, 1)
            passes_per_game = round(passes_int / games_played_int, 3)
            pass_percentage_per_game = round((passes_per_game / plays_per_game) * 100, 3)
            rushes_per_game = round(rushes_int / games_played_int, 3)
            rushes_percentage_per_game = round((rushes_per_game / plays_per_game) * 100, 3)
            
            plays_stats.append({"Team": team_name, "Plays/G": str(plays_per_game), "Pass %/G": str(pass_percentage_per_game), "Rush %/G": str(rushes_percentage_per_game)})

    # Print the extracted "Plays" stats
    for stat in plays_stats:
        print(stat)

    # Close the browser
    driver.quit()


def scrape_page(url):
    response = requests.get(url)
    response.raise_for_status()

    
    soup = bs(response.content, 'html.parser')
    table = soup.find('table', {'class': 'd3-o-table'})

    if table: 
        rows = table.find_all('tr')[1:] #skip the header row
        data = []

        for row in rows:
            columns = row.find_all('td')

            #extract name and passing yrds
            player_name = columns[0].text.strip()
            passing_yrds = columns[1].text.strip()

            data.append((player_name, passing_yrds))
        
        return data
    print("Failed to find the table. The structure of the HTML might have changed.")
    return []

    
def get_next_page(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = bs(response.content, 'html.parser')
    next_button = soup.find('a', {'class': 'nfl-o-table-pagination__next'})
    if next_button and 'href' in next_button.attrs:
        return 'https://www.nfl.com' + next_button['href']
    return None
    



def main():
   scrape_page2(url2)
   
   # base_url = 'https://www.nfl.com/stats/player-stats/category/passing/2023/REG/all/passingyards/DESC'

    #all_data = []
   # url = base_url
   # while url:
   #     page_data = scrape_page(url)
   #     all_data.extend(page_data)
   #     url = get_next_page(url)

   # with open('all_data.pkl', 'wb') as file:
   #     pickle.dump(all_data, file)
    

if __name__ == "__main__":
   main()