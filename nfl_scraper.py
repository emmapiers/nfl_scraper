import requests 
import pickle
from bs4 import BeautifulSoup as bs

from selenium import webdriver
import time

url2 = "https://www.pro-football-reference.com/years/2023/opp.htm"
url3 = "https://www.pro-football-reference.com/years/2023/passing.htm"
url4 = "https://www.pro-football-reference.com/years/2023/receiving.htm"
url5 = "https://www.pro-football-reference.com/years/2023/rushing.htm"


rb_stats = []
def scrape_team_page(url2):

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
            passes_per_game = round(passes_int / games_played_int, 1)
            pass_percentage_per_game = round((passes_per_game / plays_per_game) * 100, 1)
            rushes_per_game = round(rushes_int / games_played_int, 1)
            rushes_percentage_per_game = round((rushes_per_game / plays_per_game) * 100, 1)
            
            plays_stats.append({"Team": team_name, "Plays/G": str(plays_per_game), "Pass %/G": str(pass_percentage_per_game), "Rush %/G": str(rushes_percentage_per_game)})

    # Close the browser
    driver.quit()

    return plays_stats

def scrape_qb_page(url3):
    driver = webdriver.Safari()

    driver.get(url3)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')

    table = soup.find('table', {'id': 'passing'})

    if not table: 
        print("Table not found")
        return 
        
    # Step 5: Extract the headers from the first row of the table header
    headers = [th.get_text().strip() for th in table.thead.find_all('th')]

    player_index = headers.index("Player")
    games_index = headers.index("G")
    attempts_index = headers.index("Att")
    completions_index = headers.index("Cmp")
    yards_index = headers.index("Yds")
    tds_index = headers.index("TD")
    tds_percentage_index = headers.index("TD%")
    yards_per_attempt_index = headers.index("Y/A")

    rows = table.find('tbody').find_all('tr')
    passing_stats = []

    for row in rows[:-1]:
        columns = row.find_all('td')
        if columns:

            games_played = columns[games_index-1].getText().strip()
            players = columns[player_index-1].getText().strip()
            completions = columns[completions_index-1].getText().strip()
            attempts = columns[attempts_index -1].getText().strip()
            yards = columns[yards_index -1].getText().strip()
            tds = columns[tds_index -1].getText().strip()
            tds_percentage = columns[tds_percentage_index -1].getText().strip()
            yards_per_attempt = columns[yards_per_attempt_index -1].getText().strip()
           
            passing_stats.append({"Player": players, "Cmp": str(completions), "Att": str(attempts), "Yds": str(yards), "TD": str(tds), "TD%": str(tds_percentage), "Y/A": str(yards_per_attempt)})

    driver.quit()


    return passing_stats
    

def scrape_receiving_page(url4):
    driver = webdriver.Safari()


    driver.get(url4)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')

    table = soup.find('table', {'id': 'receiving'})

    if not table: 
        print("Table not found")
        return 
        
    # Step 5: Extract the headers from the first row of the table header
    headers = [th.get_text().strip() for th in table.thead.find_all('th')]

    player_index = headers.index("Player")
    team_index = headers.index("Tm")
    position_index = headers.index("Pos")
    games_index = headers.index("G")
    targets_index = headers.index("Tgt")
    yards_per_target_index = headers.index("Y/R")
    receptions_per_game_index = headers.index("R/G")
    yards_per_game_index = headers.index("Y/G")
    tds_per_game_index = headers.index("TD")
    


    rows = table.find('tbody').find_all('tr')
    receiving_stats = []

    for row in rows[:-1]:
        columns = row.find_all('td')
        if columns:

    
            players = columns[player_index-1].getText().strip().rstrip('*+')
            position = columns[position_index-1].getText().strip()


            if position in ["WR", "TE"]:
                team = columns[team_index-1].getText().strip()
                games_played = columns[games_index-1].getText().strip()
                targets_per_game = columns[targets_index -1].getText().strip()
                yards_per_target = columns[yards_per_target_index -1].getText().strip()
                receptions_per_game = columns[receptions_per_game_index -1].getText().strip()
                yards_per_game = columns[yards_per_game_index -1].getText().strip()
                tds_per_game = columns[tds_per_game_index -1].getText().strip()

                games_played_int = int(games_played)
                targets_per_game = int(targets_per_game)
                tds_per_game = int(tds_per_game)

                targets_per_game = round(targets_per_game / games_played_int, 1)
                tds_per_game = round(tds_per_game / games_played_int, 3)

                receiving_stats.append({
                    "Player": players, 
                    "Team": str(team),
                    "Tgt/G": str(targets_per_game), 
                    "Y/R": str(yards_per_target), 
                    "R/G": str(receptions_per_game), 
                    "Y/G": str(yards_per_game), 
                    "TD/G": str(tds_per_game)
                    })
            elif position in ["RB"]:

                team = columns[team_index-1].getText().strip()
                games_played = columns[games_index-1].getText().strip()
                targets_per_game = columns[targets_index -1].getText().strip()
                yards_per_target = columns[yards_per_target_index -1].getText().strip()
                receptions_per_game = columns[receptions_per_game_index -1].getText().strip()
                yards_per_game = columns[yards_per_game_index -1].getText().strip()
                tds_per_game = columns[tds_per_game_index -1].getText().strip()

                games_played_int = int(games_played)
                targets_per_game = int(targets_per_game)
                tds_per_game = int(tds_per_game)

                targets_per_game = round(targets_per_game / games_played_int, 1)
                tds_per_game = round(tds_per_game / games_played_int, 3)

                rb_stats.append({
                    "Player": players, 
                    "Team": str(team),
                    "Tgt/G": str(targets_per_game), 
                    "Y/R": str(yards_per_target), 
                    "R/G": str(receptions_per_game), 
                    "Y/G": str(yards_per_game), 
                    "TD/G": str(tds_per_game)
                    })


    driver.quit()


    return receiving_stats
    

def scrape_rushing_page(url5):
    # NEED STATS FROM RB_STATS
    driver = webdriver.Safari()

    driver.get(url5)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')

    table = soup.find('table', {'id': 'rushing'})

    if not table: 
        print("Table not found")
        return 
        
    # Step 5: Extract the headers from the first row of the table header
    headers = [th.get_text().strip() for th in table.thead.find_all('th')]

    player_index = headers.index("Player")
    player_index = headers.index("Player")
    team_index = headers.index("Tm")
    position_index = headers.index("Pos")
    games_index = headers.index("G")
    attempts_index = headers.index("Att")
    yards_per_att_index = headers.index("Y/A")
    tds_index = headers.index("TD")

    rows = table.find('tbody').find_all('tr')
    rushing_stats = []

    for row in rows[:-1]:
        columns = row.find_all('td')
        if columns:
           
            players = columns[player_index-5].getText().strip().rstrip('*+')
            position = columns[position_index-5].getText().strip()
            
            if position == "RB":

                team = columns[team_index-5].getText().strip()
                games_played = columns[games_index-5].getText().strip()
                attempts_per_game = columns[attempts_index -5].getText().strip()
                yards_per_att = columns[yards_per_att_index-5 ].getText().strip()
                tds_percentage = columns[tds_index -5].getText().strip()
      

                games_played_int = int(games_played)
                attempts_per_game = int(attempts_per_game)
 
                tds_percentage = int(tds_percentage)
                #Not actaully attempts per game yet or td percentage
                if (tds_percentage == 0):
                    tds_per_game = 0
                else:
                    tds_per_game = round(attempts_per_game / tds_percentage, 1)
                attempts_per_game = round(attempts_per_game / games_played_int, 1)
                

                rushing_stats.append({
                    "Player": players, 
                    "Team": str(team),
                    "Att/G": str(attempts_per_game), 
                    "Y/A": str(yards_per_att), 
                    "TD %": str(tds_per_game)
                    })
            

    driver.quit()

    return rushing_stats


def combine_rb_stats(rushing_stats, receiving_stats):
    # Define all possible columns for a player's stats
    all_columns = {
        "Player": "",
        "Team": "",
        "Att/G": "0", 
        "Y/A": "0", 
        "TD %": "0",
        "Tgt/G": "0", 
        "Y/R": "0", 
        "R/G": "0", 
        "Y/G": "0", 
        "TD/G": "0"
    }

    # Convert rushing_stats and receiving_stats to dictionaries with the player's name as the key
    rushing_dict = {stat['Player']: stat for stat in rushing_stats}
    receiving_dict = {stat['Player']: stat for stat in receiving_stats}

    # Create a combined list to hold the merged stats
    combined_stats = []

    # Combine the stats by iterating through the keys of both dictionaries
    all_players = set(rushing_dict.keys()).union(set(receiving_dict.keys()))

    for player in all_players:
        # Start with a base dictionary filled with default values (0)
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  # Set the player's name

        if player in rushing_dict:
            combined_stat.update(rushing_dict[player])

        if player in receiving_dict:
            combined_stat.update(receiving_dict[player])

        combined_stats.append(combined_stat)

    return combined_stats


def main():
    #team_data = scrape_team_page(url2)
    #with open('team_data.pkl', 'wb') as file:
    #    pickle.dump(team_data, file)


   # qb_data = scrape_qb_page(url3)
   # with open('qb_data.pkl', 'wb') as file:
   #     pickle.dump(qb_data, file)

    wr_data = scrape_receiving_page(url4)
    with open('wr_data.pkl', 'wb')as file:
        pickle.dump(wr_data, file)

    rb_data = scrape_rushing_page(url5)
    
    rb_combined_data = combine_rb_stats(rb_data, rb_stats)

    with open('rb_data.pkl', 'wb') as file:
        pickle.dump(rb_combined_data, file)

if __name__ == "__main__":
   main()