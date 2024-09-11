import requests 
import pickle
from bs4 import BeautifulSoup as bs
import pandas as pd

from selenium import webdriver
import time

url2 = "https://www.pro-football-reference.com/years/2023/opp.htm"
url3 = "https://www.pro-football-reference.com/years/2023/passing.htm"
url4 = "https://www.pro-football-reference.com/years/2023/receiving.htm"
url5 = "https://www.pro-football-reference.com/years/2023/rushing.htm"
url6 = "https://www.pro-football-reference.com/years/2023/#all_rushing"
url7 = "https://www.pro-football-reference.com/years/2023/#all_team_stats"


rb_stats = []
qb_rushing_stats = []
team_rushing_stats = []
qb_passing_stats = []

team_shorthand_to_full = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GNB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KAN": "Kansas City Chiefs",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "LVR": "Las Vegas Raiders",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NWE": "New England Patriots",
    "NOR": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SFO": "San Francisco 49ers",
    "SEA": "Seattle Seahawks",
    "TAM": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders"
}

def scrap_team_offence_page(url7):
    driver = webdriver.Safari()

    driver.get(url7)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')  

    offense_div = soup.find('div', {'id': 'all_team_stats'})
    if offense_div:
        # Now look for the table within the rushing_div
        table = offense_div.find('table')
        if not table:
            print("Table not found within the div")
            return
    else:
        print("Div with id 'all_rushing' not found")
    
    header_row = table.find('tr', class_=lambda x: x != 'over_header')

    # Extract the headers from that 'tr'
    headers = [th.getText().strip() for th in header_row.find_all('th')]


    team_index = headers.index("Tm")
    games_index = headers.index("G")
    plays_index = headers.index("Ply")
    passing_attempts_index = headers.index("Att")


    att_indices = [i for i, header in enumerate(headers) if header == "Att"]
    if len(att_indices) > 1:
        rush_attempts_index = att_indices[1]

    rows = table.find('tbody').find_all('tr')
    plays_stats = []

    for row in rows[:]:
        columns = row.find_all('td')
        if columns:
            team_name = columns[0].getText().strip()
            games_played = int(columns[games_index-1].getText().strip())
            plays = int(columns[plays_index-1].getText().strip())
            passes = int(columns[passing_attempts_index-1].getText().strip())
            rushes = int(columns[rush_attempts_index -1].getText().strip())

            plays_per_game = round(plays / games_played, 1)
            passes_per_game = round(passes / games_played, 1)
            pass_percentage_per_game = round((passes_per_game / plays_per_game) * 100, 1)
            rushes_per_game = round(rushes/ games_played, 1)
            rushes_percentage_per_game = round((rushes_per_game / plays_per_game) * 100, 1)

            plays_stats.append({
                "Team": team_name, 
                "Plays/G": float(plays_per_game), 
                "Pass %/G": float(pass_percentage_per_game), 
                "Rush %/G": float(rushes_percentage_per_game)
                })
   
            
    driver.quit()

    return plays_stats

def scrap_team_rushing_page(url6):
    driver = webdriver.Safari()

    driver.get(url6)
    driver.implicitly_wait(10)
    
    html = driver.page_source
    soup = bs(html, 'html.parser')   

    rushing_div = soup.find('div', {'id': 'all_rushing'})
    
    if rushing_div:
        # Now look for the table within the rushing_div
        table = rushing_div.find('table')
        if not table:
            print("Table not found within the div")
            return
    else:
        print("Div with id 'all_rushing' not found")

    headers = [th.get_text().strip() for th in table.thead.find_all('th')]

    team_index = headers.index("Tm")
    attempts_index = headers.index("Att")

    rows = table.find('tbody').find_all('tr')
    

    for row in rows[:-1]:
        columns = row.find_all('td')
        if columns:

            team = columns[team_index-1].getText().strip()
            attempts = columns[attempts_index-1].getText().strip()


        team_rushing_stats.append({
            "Team": team, 
            "Att": int(attempts)
        })


    # Close the browser after scraping
    driver.quit()

def scrape_team_defense_page(url2):

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
            
            plays_stats.append({
                "Team": team_name, 
                "Plays/G AG": float(plays_per_game), 
                "Pass %/G AG": float(pass_percentage_per_game), 
                "Rush %/G AG": float(rushes_percentage_per_game)
                })

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
    team_index = headers.index("Team")
    position_index = headers.index("Pos")
    games_index = headers.index("G")
    attempts_index = headers.index("Att")
    completions_index = headers.index("Cmp")
    yards_index = headers.index("Yds")
    tds_index = headers.index("TD")
    tds_percentage_index = headers.index("TD%")
    yards_per_attempt_index = headers.index("Y/A")

    rows = table.find('tbody').find_all('tr')


    for row in rows[:-1]:
        columns = row.find_all('td')
        if columns:

            position = columns[position_index-1].getText().strip()
        
            if position == 'QB':
                games_played = int(columns[games_index-1].getText().strip())
                team = columns[team_index-1].getText().strip()
                players = columns[player_index-1].getText().strip()
                completions = columns[completions_index-1].getText().strip()
                attempts = columns[attempts_index -1].getText().strip()
                yards = columns[yards_index -1].getText().strip()
                tds = columns[tds_index -1].getText().strip()
                tds_percentage = columns[tds_percentage_index -1].getText().strip()
                yards_per_attempt = columns[yards_per_attempt_index -1].getText().strip()

                cmp_per_game = round(int(completions) / games_played, 1)
                att_per_game = round(int(attempts) / games_played, 1)
                yds_per_game = round(int(yards) / games_played, 1)
                tds_per_game = round(int(tds) / games_played, 1)
            
                qb_passing_stats.append({
                    "Player": players, 
                    "Team": str(team),
                    "Cmp/G": int(cmp_per_game), 
                    "Att/G": int(att_per_game), 
                    "Yds/G": int(yds_per_game), 
                    "TD/G": int(tds_per_game), 
                    "TD%": str(tds_percentage), 
                    "Y/A": str(yards_per_attempt)
                    })

    driver.quit()



    return qb_passing_stats
    
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
                    "Tgt/G": int(targets_per_game), 
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
                games_played = int(columns[games_index-5].getText().strip())
                attempts = int(columns[attempts_index -5].getText().strip())
                yards_per_att = columns[yards_per_att_index-5 ].getText().strip()
                tds_percentage = int(columns[tds_index -5].getText().strip())

                if (tds_percentage == 0):
                    tds_per_game = 0.0
                else:
                    tds_per_game = round(attempts / tds_percentage, 1)
                attempts_per_game = round(attempts / games_played, 1)
                

                rushing_stats.append({
                    "Player": players, 
                    "Team": str(team),
                    "Att": str(attempts),
                    "Att/G": str(attempts_per_game), 
                    "Y/Carry": str(yards_per_att), 
                    "TD %": str(tds_per_game)
                    })
            elif position == "QB":
                yards_per_att = columns[yards_per_att_index-5 ].getText().strip()
                attempts = columns[attempts_index -5].getText().strip()
                team = columns[team_index-5].getText().strip()

                qb_rushing_stats.append({
                    "Player": players, 
                    "Team": team,
                    "Yds/Carry": str(yards_per_att), 
                    "Att": str(attempts)

                })
            

    driver.quit()

    return rushing_stats

def combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats):
    all_columns = {
        "Player": "",
        "Team": "",
        "Cmp/G": 0,
        "Att/G": 0, 
        "Yds/G": 0,
        "TD/G": 0.0,
        "TD%": 0.0,
        "Y/A": 0.0, 
        "Carry %": 0.0, 
        "Yds/Carry": 0,
    }
    # Initialize combined stats list
    combined_stats = []

    rushing_dict =  {stat['Player']: stat for stat in qb_rushing_stats}
    passing_dict = {stat['Player']: stat for stat in qb_passing_stats}

    team_rushing_dict = {team_stat['Team']: team_stat['Att'] for team_stat in team_rushing_stats}
    
    all_players = set(rushing_dict.keys()).union(set(passing_dict.keys()))

    for player in all_players:
        # Start with a base dictionary filled with default values (0)
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  # Set the player's name

        if player in rushing_dict:
            for key, value in rushing_dict[player].items():
                combined_stat[key] = value if value is not None else "0"

        if player in passing_dict:
            for key, value in passing_dict[player].items():
                combined_stat[key] = value if value is not None else "0"


        if player in rushing_dict:
            player_team_shorthand = rushing_dict[player]["Team"] 
            player_att = float(rushing_dict[player]["Att"])
            
            full_team_name = team_shorthand_to_full.get(player_team_shorthand)

            if full_team_name and full_team_name in team_rushing_dict:
                team_att = float(team_rushing_dict[full_team_name])  # Full team's rushing attempts
                
                # Calculate Carry % as (player_att / team_att) * 100
                carry_percentage = (player_att / team_att) * 100
                combined_stat["Carry %"] = f"{carry_percentage:.2f}"  # Format to 2 decimal places


        combined_stats.append(combined_stat)

    return combined_stats
                      
def combine_rb_stats(rushing_stats, receiving_stats):
    # Define all possible columns for a player's stats
    all_columns = {
        "Player": "",
        "Team": "",
        "Att/G": 0, 
        "Carry %": 0.0,
        "Y/Carry": 0.0, 
        "TD %": 0.0,
        "Tgt/G": 0, 
        "Y/R": 0, 
        "R/G": 0, 
        "Y/G": 0, 
        "TD/G": 0
    }

    # Convert rushing_stats and receiving_stats to dictionaries with the player's name as the key
    rushing_dict = {stat['Player']: stat for stat in rushing_stats}
    receiving_dict = {stat['Player']: stat for stat in receiving_stats}

    team_rushing_dict = {team_stat['Team']: team_stat['Att'] for team_stat in team_rushing_stats}

    # Create a combined list to hold the merged stats
    combined_stats = []
    all_players = set(rushing_dict.keys()).union(set(receiving_dict.keys()))

    for player in all_players:
        # Start with a base dictionary filled with default values (0)
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  # Set the player's name
        # Combine the stats by iterating through the keys of both dictionaries
        all_players = set(rushing_dict.keys()).union(set(receiving_dict.keys()))

        if player in rushing_dict:
            combined_stat.update(rushing_dict[player])  # Update with player's rushing stats

        if player in receiving_dict:
            combined_stat.update(receiving_dict[player])  # Update with player's receiving stats

        # If the player has rushing stats, calculate Carry % (Player's Att / Team's Att)
        if player in rushing_dict:
            player_team_shorthand = rushing_dict[player]["Team"]
            player_att = float(rushing_dict[player].get("Att", "0"))  # Default to 0 if missing
                
            # Convert team shorthand to full team name
            full_team_name = team_shorthand_to_full.get(player_team_shorthand)

            if full_team_name and full_team_name in team_rushing_dict:
                team_att = float(team_rushing_dict.get(full_team_name, "0"))  # Default to 0 if missing
                
                # Calculate Carry % as (player_att / team_att) * 100
                if team_att > 0:  # Avoid division by zero
                    carry_percentage = (player_att / team_att) * 100
                else:
                    carry_percentage = 0.0
                    
                combined_stat["Carry %"] = f"{carry_percentage:.2f}"  # Format to 2 decimal places

        combined_stats.append(combined_stat)

    return combined_stats


def combine_team_stats(offense_data, defense_data):
    combined_list = []
    
    # Loop through offense data
    for offense_item in offense_data:
        team_name = offense_item['Team']
        
        # Find the corresponding defense entry
        matching_defense_item = next((item for item in defense_data if item['Team'] == team_name), None)
        
        if matching_defense_item:
            # Merge the two dictionaries if both exist
            combined_item = {**offense_item, **matching_defense_item}
        else:
            # If no matching defense data, just use offense data
            combined_item = offense_item
        
        combined_list.append(combined_item)
    
    return combined_list


def main():
    '''
    #QB DATA
    scrap_team_rushing_page(url6)
    scrape_qb_page(url3)
    scrape_rushing_page(url5)
    qb_data = combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats)

    with open('qb_data.pkl', 'wb') as file:
        pickle.dump(qb_data, file)
    
    #TEAM DATA
    offense_data = scrap_team_offence_page(url7)
    defense_data = scrape_team_defense_page(url2)

    team_data = combine_team_stats(offense_data, defense_data)
    with open('team_data.pkl', 'wb') as file:
        pickle.dump(team_data, file)
 
    #WR DATA
    wr_data = scrape_receiving_page(url4)
    with open('wr_data.pkl', 'wb')as file:
        pickle.dump(wr_data, file)

    #RB DATA
    rb_data = scrape_rushing_page(url5)
    
    rb_combined_data = combine_rb_stats(rb_data, rb_stats)
    with open('rb_data.pkl', 'wb') as file:
        pickle.dump(rb_combined_data, file)
   '''
 
def excel_maker():
    
    #QB DATA
    scrap_team_rushing_page(url6)
    scrape_qb_page(url3)
    scrape_rushing_page(url5)
    qb_data = combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats)

    df_qb = pd.DataFrame(qb_data)
    df_qb['TD%'] = pd.to_numeric(df_qb['TD%'], errors='coerce')
    df_qb['Y/A'] = pd.to_numeric(df_qb['Y/A'], errors='coerce')
    df_qb['Carry %'] = pd.to_numeric(df_qb['Carry %'], errors='coerce')
    df_qb['Yds/Carry'] = pd.to_numeric(df_qb['Yds/Carry'], errors='coerce')
    df_qb['Att'] = pd.to_numeric(df_qb['Att'], errors='coerce')
    
    df_qb.fillna(0, inplace=True)
    
    #TEAM DATA
    offense_data = scrap_team_offence_page(url7)
    defense_data = scrape_team_defense_page(url2)

    team_data = combine_team_stats(offense_data, defense_data)
    
    df_team = pd.DataFrame(team_data)

    df_team['Plays/G'] = pd.to_numeric(df_team['Plays/G'], errors='coerce')
    df_team['Pass %/G'] = pd.to_numeric(df_team['Pass %/G'], errors='coerce')
    df_team['Rush %/G'] = pd.to_numeric(df_team['Rush %/G'], errors='coerce')
    df_team['Plays/G AG'] = pd.to_numeric(df_team['Plays/G AG'], errors='coerce')
    df_team['Pass %/G AG'] = pd.to_numeric(df_team['Pass %/G AG'], errors='coerce')
    df_team['Rush %/G AG'] = pd.to_numeric(df_team['Rush %/G AG'], errors='coerce')

    df_team.fillna(0, inplace=True)

    #WR DATA
    wr_data = scrape_receiving_page(url4)
    df_wr = pd.DataFrame(wr_data)

    df_wr['Tgt/G'] = pd.to_numeric(df_wr['Tgt/G'], errors='coerce')
    df_wr['Y/R'] = pd.to_numeric(df_wr['Y/R'], errors='coerce')
    df_wr['R/G'] = pd.to_numeric(df_wr['R/G'], errors='coerce')
    df_wr['Y/G'] = pd.to_numeric(df_wr['Y/G'], errors='coerce')
    df_wr['TD/G'] = pd.to_numeric(df_wr['TD/G'], errors='coerce')

    df_wr.fillna(0, inplace=True)

    #RB DATA
    rb_single_data = scrape_rushing_page(url5)
    
    rb_data = combine_rb_stats(rb_single_data, rb_stats)
    df_rb = pd.DataFrame(rb_data)

    df_rb['Att/G'] = pd.to_numeric(df_rb['Att/G'], errors='coerce')
    df_rb['Carry %'] = pd.to_numeric(df_rb['Carry %'], errors='coerce')
    df_rb['Y/Carry'] = pd.to_numeric(df_rb['Y/Carry'], errors='coerce')
    df_rb['TD %'] = pd.to_numeric(df_rb['TD %'], errors='coerce')
    df_rb['Tgt/G'] = pd.to_numeric(df_rb['Tgt/G'], errors='coerce')
    df_rb['Y/R'] = pd.to_numeric(df_rb['Y/R'], errors='coerce')
    df_rb['R/G'] = pd.to_numeric(df_rb['R/G'], errors='coerce')
    df_rb['Y/G'] = pd.to_numeric(df_rb['Y/G'], errors='coerce')
    df_rb['TD/G'] = pd.to_numeric(df_rb['TD/G'], errors='coerce')
    df_rb['Att'] = pd.to_numeric(df_rb['Att'], errors='coerce')
 
    df_rb.fillna(0, inplace=True)



    with pd.ExcelWriter("nfl_stats.xlsx", engine="xlsxwriter") as writer:
        # Write each DataFrame to a different sheet/tab
        df_team.to_excel(writer, sheet_name="Team Stats", index=False)
        df_qb.to_excel(writer, sheet_name="QB Stats", index=False)
        df_wr.to_excel(writer, sheet_name="WR Stats", index=False)
        df_rb.to_excel(writer, sheet_name="RB Stats", index=False)



if __name__ == "__main__":
   main()
   excel_maker()