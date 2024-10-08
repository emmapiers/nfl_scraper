import requests 
import pickle
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

from datetime import datetime

from selenium import webdriver
import time
import re

url2 = "https://www.pro-football-reference.com/years/2023/opp.htm"
url3 = "https://www.pro-football-reference.com/years/2023/passing.htm"
url4 = "https://www.pro-football-reference.com/years/2023/receiving.htm"
url5 = "https://www.pro-football-reference.com/years/2023/rushing.htm"
url6 = "https://www.pro-football-reference.com/years/2023/#all_rushing"
url7 = "https://www.pro-football-reference.com/years/2023/#all_team_stats"
url8 = "https://www.fantasypros.com/nfl/advanced-stats-wr.php?year=2023"
url9 = "https://www.fantasypros.com/nfl/advanced-stats-te.php?year=2023"
url10 = "https://www.pro-football-reference.com/years/2023/fantasy-points-against-RB.htm"
url11 = "https://www.pro-football-reference.com/years/2023/fantasy-points-against-QB.htm"
url12 = "https://www.pro-football-reference.com/years/2023/fantasy-points-against-WR.htm"
url13 = "https://www.pro-football-reference.com/years/2023/fantasy-points-against-TE.htm"



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

round_to_date = {
    #Weeks start on Tuesdays and end on Mondays
    1: ('2024-09-05', '2024-09-09'), 
    2: ('2024-09-10', '2024-09-16'), 
    3: ('2024-09-17', '2024-09-23'), 
    4: ('2024-09-24', '2024-09-30'), 
    5: ('2024-10-01', '2024-10-07'), 
    6: ('2024-10-08', '2024-10-14'), 
    7: ('2024-10-15', '2024-10-21'), 
    8: ('2024-10-22', '2024-10-28'), 
    9: ('2024-10-29', '2024-11-04'), 
    10: ('2024-11-05', '2024-11-11'), 
    11: ('2024-11-12', '2024-11-18'), 
    12: ('2024-11-19', '2024-11-25'), 
    13: ('2024-11-26', '2024-12-02'), 
    14: ('2024-12-03', '2024-12-09'), 
    15: ('2024-12-10', '2024-12-16'), 
    16: ('2024-12-17', '2024-12-23'), 
    17: ('2024-12-24', '2024-12-30'), 
    18: ('2025-12-31', '2025-01-05'), 
}

rb_stats = []
qb_rushing_stats = []
team_rushing_stats = []
qb_passing_stats = []

def scrap_team_offence_page(url7):
    full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
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

            shorthand_name = full_to_shorthand.get(team_name, team_name)  # Use full name if shorthand not found
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
                "Team": shorthand_name, 
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
    full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
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

            shorthand_name = full_to_shorthand.get(team_name, team_name)
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
                "Team": shorthand_name, 
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
                    "Cmp/G": str(cmp_per_game), 
                    "Att/G": str(att_per_game), 
                    "Yds/G": str(yds_per_game), 
                    "TD/G": str(tds_per_game), 
                    "TD%": str(tds_percentage), 
                    "Y/A": str(yards_per_attempt)
                    })

    driver.quit()



    return qb_passing_stats

def scrape_target_percentage(url_wr, url_te):
    # WR
    response = requests.get(url_wr)
    soup = bs(response.content, 'html.parser')

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
                    "Position": 'WR',
                    "TM %": tm_percentage
                })
    # TE
    response = requests.get(url_te)
    soup = bs(response.content, 'html.parser')

    # Find the table with id 'data'
    table = soup.find('table', {'id': 'data'})
    

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
                    "Position": 'TE',
                    "TM %": tm_percentage
                })
    

    return player_data
  
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
                    "Position": str(position),
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

def combine_wr_te_stats():
    # Scrape TM % for WR and TE
    wr_te_tm_data = scrape_target_percentage(url8, url9)

    receiving_data = scrape_receiving_page(url4)

    all_columns = {
        "Player": "",
        "Team": "",
        "Position": "",
        "Tgt/G": 0.0, 
        "Y/R": 0.0,
        "R/G": 0.0, 
        "Y/G": 0.0, 
        "TD/G": 0.0,
        "TM %": 0.0  # Default value for target percentage
    }
    # Merge TM % with receiving stats based on Player name
    combined_stats = []
    # Normalize player names and exclude unwanted players
    tm_percentage_dict = {}
    for stat in wr_te_tm_data:
        normalized_name = normalize_player_name(stat['Player'])
        if normalized_name is not None:
            tm_percentage_dict[normalized_name] = stat
    
    receiving_dict = {}
    for stat in receiving_data:
        normalized_name = normalize_player_name(stat['Player'])
        if normalized_name is not None:
            receiving_dict[normalized_name] = stat

    # Get all unique player names from both datasets
    all_players = set(tm_percentage_dict.keys()).union(set(receiving_dict.keys()))
    

    # Combine stats for each player
    for player in all_players:
        # Start with a base dictionary filled with default values
        combined_stat = all_columns.copy()
        combined_stat["Player"] = player  # Set the player's name

        # Add receiving stats if available
        if player in receiving_dict:
            for key, value in receiving_dict[player].items():
                combined_stat[key] = value if value is not None else 0

        # Add TM % if available
        if player in tm_percentage_dict:
            combined_stat["TM %"] = convert_tm_percentage(tm_percentage_dict[player].get("TM %", "N/A"))
            combined_stat["Position"] = tm_percentage_dict[player].get("Position", "")

        # Add the combined stat to the list
        combined_stats.append(combined_stat)

    return combined_stats

def convert_tm_percentage(value):
    # Check if the value contains a % and convert to float
    if isinstance(value, str) and "%" in value:
        return float(value.replace("%", "").strip())
    return value  # Return the value as-is if it's already correct

def normalize_player_name(player_name):
    # Standardize specific player names
    name_corrections = {
        "DJ Chark Jr.": "DJ Chark",
        "Scotty Miller": "Scott Miller",
        "Deebo Samuel Sr.": "Deebo Samuel",
        "Mecole Hardman Jr.": "Mecole Hardman",
        "Steven Sims Jr.": "Steven Sims",
        "Trent Sherfield Sr.": "Trent Sherfield",
        "James Proche II": "James Proche",
        "Gabe Davis": "Gabriel Davis",
        "Ray-Ray McCloud III": "Ray-Ray McCloud",
        "DeMario Douglas": "Demario Douglas",
        "Andrew Beck": None,
        "DK Metcalf": "D.K. Metcalf",
        "Chig Okonkwo": "Chigoziem Okonkwo",
        "Donald Parham Jr.": "Donald Parham",
        "Calvin Austin III": "Calvin Austin",
        "Taysom Hill": None,
        "John Metchie III": "John Metchie",
        "Allen Robinson II": "Allen Robinson",
        "Marvin Mims Jr.": "Marvin Mims",
        "Drew Ogletree": "Andrew Ogletree",
        "DJ Moore": "David Moore", 
        "Richie James Jr.": "Richie James", 
        "Marvin Jones Jr.": "Marvin Jones", 
        "Joshua Palmer": "Josh Palmer"
    }
    if player_name in name_corrections:
        normalized_name = name_corrections[player_name]
    else:
        normalized_name = player_name

    return normalized_name

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
                if key != "Att":
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
            for key, value in rushing_dict[player].items():
                if key != "Att":  # Skip the 'Att' key to avoid adding it to combined_stat
                    combined_stat[key] = value if value is not None else 0

        if player in receiving_dict:
            for key, value in receiving_dict[player].items():
                combined_stat[key] = value if value is not None else 0

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

def combine_team_stats(offense_data, defense_data, dk_points_data):
    combined_list = []

    # Reverse the dictionary to map full names to shorthand
    team_full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    # Convert dk_points_data team names to shorthand
    for dk_item in dk_points_data:
        full_name = dk_item['Team']
        dk_item['Team'] = team_full_to_shorthand.get(full_name, full_name)

    # Loop through offense data
    for offense_item in offense_data:
        team_name = offense_item['Team']
        
        # Find the corresponding defense entry
        matching_defense_item = next((item for item in defense_data if item['Team'] == team_name), None)
        
        # Find the corresponding DK Points entry
        matching_dk_points_item = next((item for item in dk_points_data if item['Team'] == team_name), None)
        
        # Merge offense and defense data
        combined_item = {**offense_item}
        if matching_defense_item:
            combined_item.update(matching_defense_item)
        
        # Add DK Points if available
        if matching_dk_points_item:
            combined_item.update(matching_dk_points_item)
        
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
    dk_points_data = 

    team_data = combine_team_stats(offense_data, defense_data, dk_points_data)
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
 
def make_qb_sheet():
    #QB DATA
    scrap_team_rushing_page(url6)
    scrape_qb_page(url3)
    scrape_rushing_page(url5)
    qb_data = combine_qb_stats(qb_rushing_stats, qb_passing_stats, team_rushing_stats)

    df_qb = pd.DataFrame(qb_data)
    df_qb['Cmp/G'] = pd.to_numeric(df_qb['TD%'], errors='coerce')
    df_qb['Att/G'] = pd.to_numeric(df_qb['Y/A'], errors='coerce')
    df_qb['Yds/G'] = pd.to_numeric(df_qb['Carry %'], errors='coerce')
    df_qb['TD/G'] = pd.to_numeric(df_qb['Yds/Carry'], errors='coerce')
    df_qb['TD%'] = pd.to_numeric(df_qb['TD%'], errors='coerce')
    df_qb['Y/A'] = pd.to_numeric(df_qb['Y/A'], errors='coerce')
    df_qb['Carry %'] = pd.to_numeric(df_qb['Carry %'], errors='coerce')
    df_qb['Yds/Carry'] = pd.to_numeric(df_qb['Yds/Carry'], errors='coerce')
    
    df_qb.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_qb = pd.merge(df_qb, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Home Team Shorthand', how='left')

    df_qb = pd.merge(df_qb, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Away Team Shorthand', how='left')

    # Combine the shorthand columns and find opponent
    df_qb['Home Team Shorthand'] = df_qb['Home Team Shorthand_x'].combine_first(df_qb['Home Team Shorthand_y'])
    df_qb['Away Team Shorthand'] = df_qb['Away Team Shorthand_x'].combine_first(df_qb['Away Team Shorthand_y'])

    df_qb.drop(columns=['Home Team Shorthand_x', 'Home Team Shorthand_y', 
                        'Away Team Shorthand_x', 'Away Team Shorthand_y'], inplace=True)

    # Find the opponent team shorthand
    df_qb['Opponent Team Shorthand'] = np.where(df_qb['Home Team Shorthand'] == df_qb['Team'],
                                                df_qb['Away Team Shorthand'], df_qb['Home Team Shorthand'])

    df_qb.drop(columns=['Home Team Shorthand', 'Away Team Shorthand'], inplace=True)
    df_qb.rename(columns={'Opponent Team Shorthand': 'Weekly Opponent'}, inplace=True)
    
    # Merge QB data with team stats of the opponent
    
    df_team = make_team_sheet()

    team_full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    df_team['Team'] = df_team['Team'].map(team_full_to_shorthand).fillna(df_team['Team'])


    # Now merge using the converted long-hand team names
    df_final = pd.merge(df_qb, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final
    
def make_team_sheet():
    #TEAM DATA
    offense_data = scrap_team_offence_page(url7)
    defense_data = scrape_team_defense_page(url2)
    dk_points_data = merge_dk_team_data(url10, url11, url12, url13)

    team_data = combine_team_stats(offense_data, defense_data, dk_points_data)
    
    df_t = pd.DataFrame(team_data)
    

    df_t['Plays/G'] = pd.to_numeric(df_t['Plays/G'], errors='coerce')
    df_t['Pass %/G'] = pd.to_numeric(df_t['Pass %/G'], errors='coerce')
    df_t['Rush %/G'] = pd.to_numeric(df_t['Rush %/G'], errors='coerce')
    df_t['Plays/G AG'] = pd.to_numeric(df_t['Plays/G AG'], errors='coerce')
    df_t['Pass %/G AG'] = pd.to_numeric(df_t['Pass %/G AG'], errors='coerce')
    df_t['Rush %/G AG'] = pd.to_numeric(df_t['Rush %/G AG'], errors='coerce')
    df_t['Rush %/G AG'] = pd.to_numeric(df_t['Rush %/G AG'], errors='coerce')
    df_t['DKPt Against RB'] = pd.to_numeric(df_t['DKPt Against RB'], errors='coerce')
    df_t['DKPt Against WR'] = pd.to_numeric(df_t['DKPt Against WR'], errors='coerce')
    df_t['DKPt Against QB'] = pd.to_numeric(df_t['DKPt Against QB'], errors='coerce')
    df_t['DKPt Against TE'] = pd.to_numeric(df_t['DKPt Against TE'], errors='coerce')

    df_t.fillna(0, inplace=True)

    return df_t

def make_full_team_sheet():
    #TEAM DATA
    offense_data = scrap_team_offence_page(url7)
    defense_data = scrape_team_defense_page(url2)
    dk_points_data = merge_dk_team_data(url10, url11, url12, url13)

    team_data = combine_team_stats(offense_data, defense_data, dk_points_data)
    
    df_t = pd.DataFrame(team_data)
    
    df_t['Plays/G'] = pd.to_numeric(df_t['Plays/G'], errors='coerce')
    df_t['Pass %/G'] = pd.to_numeric(df_t['Pass %/G'], errors='coerce')
    df_t['Rush %/G'] = pd.to_numeric(df_t['Rush %/G'], errors='coerce')
    df_t['Plays/G AG'] = pd.to_numeric(df_t['Plays/G AG'], errors='coerce')
    df_t['Pass %/G AG'] = pd.to_numeric(df_t['Pass %/G AG'], errors='coerce')
    df_t['Rush %/G AG'] = pd.to_numeric(df_t['Rush %/G AG'], errors='coerce')
    df_t['DKPt Against RB'] = pd.to_numeric(df_t['DKPt Against RB'], errors='coerce')
    df_t['DKPt Against WR'] = pd.to_numeric(df_t['DKPt Against WR'], errors='coerce')
    df_t['DKPt Against QB'] = pd.to_numeric(df_t['DKPt Against QB'], errors='coerce')
    df_t['DKPt Against TE'] = pd.to_numeric(df_t['DKPt Against TE'], errors='coerce')


    df_t.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_team = df_t.copy()

    df_t = pd.merge(df_t, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Home Team Shorthand', how='left')

    df_t = pd.merge(df_t, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Away Team Shorthand', how='left')

    # Combine the shorthand columns and find opponent
    df_t['Home Team Shorthand'] = df_t['Home Team Shorthand_x'].combine_first(df_t['Home Team Shorthand_y'])
    df_t['Away Team Shorthand'] = df_t['Away Team Shorthand_x'].combine_first(df_t['Away Team Shorthand_y'])

    df_t.drop(columns=['Home Team Shorthand_x', 'Home Team Shorthand_y', 
                        'Away Team Shorthand_x', 'Away Team Shorthand_y'], inplace=True)

    # Find the opponent team shorthand
    df_t['Opponent Team Shorthand'] = np.where(df_t['Home Team Shorthand'] == df_t['Team'],
                                                df_t['Away Team Shorthand'], df_t['Home Team Shorthand'])

    df_t.drop(columns=['Home Team Shorthand', 'Away Team Shorthand'], inplace=True)
    df_t.rename(columns={'Opponent Team Shorthand': 'Weekly Opponent'}, inplace=True)
    
    # Merge QB data with team stats of the opponent


    team_full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    df_team['Team'] = df_team['Team'].map(team_full_to_shorthand).fillna(df_team['Team'])


    # Now merge using the converted long-hand team names
    df_final = pd.merge(df_t, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    for col in df_final.columns:
        if '_x' in col:
            df_final[col.replace('_x', '')] = df_final[col]
        if '_y' in col:
            df_final.drop(columns=[col], inplace=True)


    return df_final

def make_wr_sheet():
    #WR DATA
    wr_data = combine_wr_te_stats()
    df_wr = pd.DataFrame(wr_data)


    df_wr['TM %'] = pd.to_numeric(df_wr['TM %'], errors='coerce')
    df_wr['Tgt/G'] = pd.to_numeric(df_wr['Tgt/G'], errors='coerce')
    df_wr['Y/R'] = pd.to_numeric(df_wr['Y/R'], errors='coerce')
    df_wr['R/G'] = pd.to_numeric(df_wr['R/G'], errors='coerce')
    df_wr['Y/G'] = pd.to_numeric(df_wr['Y/G'], errors='coerce')
    df_wr['TD/G'] = pd.to_numeric(df_wr['TD/G'], errors='coerce')

    df_wr.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_wr = pd.merge(df_wr, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Home Team Shorthand', how='left')

    df_wr = pd.merge(df_wr, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Away Team Shorthand', how='left')

    # Combine the shorthand columns and find opponent
    df_wr['Home Team Shorthand'] = df_wr['Home Team Shorthand_x'].combine_first(df_wr['Home Team Shorthand_y'])
    df_wr['Away Team Shorthand'] = df_wr['Away Team Shorthand_x'].combine_first(df_wr['Away Team Shorthand_y'])

    df_wr.drop(columns=['Home Team Shorthand_x', 'Home Team Shorthand_y', 
                        'Away Team Shorthand_x', 'Away Team Shorthand_y'], inplace=True)

    # Find the opponent team shorthand
    df_wr['Opponent Team Shorthand'] = np.where(df_wr['Home Team Shorthand'] == df_wr['Team'],
                                                df_wr['Away Team Shorthand'], df_wr['Home Team Shorthand'])

    df_wr.drop(columns=['Home Team Shorthand', 'Away Team Shorthand'], inplace=True)
    df_wr.rename(columns={'Opponent Team Shorthand': 'Weekly Opponent'}, inplace=True)
    
    # Merge QB data with team stats of the opponent
    
    df_team = make_team_sheet()

    team_full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    df_team['Team'] = df_team['Team'].map(team_full_to_shorthand).fillna(df_team['Team'])


    # Now merge using the converted long-hand team names
    df_final = pd.merge(df_wr, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final

def make_rb_sheet():
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

 
    df_rb.fillna(0, inplace=True)

    games_for_cur_round = find_matchups()

    df_rb = pd.merge(df_rb, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Home Team Shorthand', how='left')

    df_rb = pd.merge(df_rb, games_for_cur_round[['Home Team Shorthand', 'Away Team Shorthand']],
                     left_on='Team', right_on='Away Team Shorthand', how='left')

    # Combine the shorthand columns and find opponent
    df_rb['Home Team Shorthand'] = df_rb['Home Team Shorthand_x'].combine_first(df_rb['Home Team Shorthand_y'])
    df_rb['Away Team Shorthand'] = df_rb['Away Team Shorthand_x'].combine_first(df_rb['Away Team Shorthand_y'])

    df_rb.drop(columns=['Home Team Shorthand_x', 'Home Team Shorthand_y', 
                        'Away Team Shorthand_x', 'Away Team Shorthand_y'], inplace=True)

    # Find the opponent team shorthand
    df_rb['Opponent Team Shorthand'] = np.where(df_rb['Home Team Shorthand'] == df_rb['Team'],
                                                df_rb['Away Team Shorthand'], df_rb['Home Team Shorthand'])

    df_rb.drop(columns=['Home Team Shorthand', 'Away Team Shorthand'], inplace=True)
    df_rb.rename(columns={'Opponent Team Shorthand': 'Weekly Opponent'}, inplace=True)
    
    # Merge QB data with team stats of the opponent
    
    df_team = make_team_sheet()

    team_full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    df_team['Team'] = df_team['Team'].map(team_full_to_shorthand).fillna(df_team['Team'])


    # Now merge using the converted long-hand team names
    df_final = pd.merge(df_rb, df_team, left_on='Weekly Opponent', right_on='Team', how='left')

    df_final.rename(columns={'Team_x': 'Team'}, inplace=True)
    df_final.drop(columns=['Team_y'], inplace=True)

    return df_final

def scrape_dk_points(url, position):
    # Full to shorthand dictionary
    full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}
    
    driver = webdriver.Safari()
    driver.get(url)
    driver.implicitly_wait(10)

    # Parse the page with BeautifulSoup
    html = driver.page_source
    soup = bs(html, 'html.parser')

    # Find the table with fantasy points data
    table = soup.find('table', {'id': 'fantasy_def'})
    
    if not table:
        print(f"Table for {position} not found")
        driver.quit()
        return None

    dk_points_stats = []

    rows = table.find_all('tr')
    for row in rows:
        headers = row.find_all('th', {'data-stat': 'team'})
        if headers:  # if there is a 'th' tag with team data
            team = headers[0].text.strip()  # Team name
            cols = row.find_all('td')
            if cols:
                dkpt = cols[-2].text.strip()  # DKPt column (second last column)
                
                dk_points_stats.append({
                    "Team": team,
                    f"DKPt Against {position}": dkpt
                })

    driver.quit()
    
    return dk_points_stats

def merge_dk_team_data(rb_url, qb_url, wr_url, te_url):
    # Scrape data for each position
    rb_data = scrape_dk_points(rb_url, 'RB')
    qb_data = scrape_dk_points(qb_url, 'QB')
    wr_data = scrape_dk_points(wr_url, 'WR')
    te_data = scrape_dk_points(te_url, 'TE')
    merged_data = {}

    # Add RB data
    for entry in rb_data:
        team = entry["Team"]
        merged_data[team] = {"Team": team, "DKPt Against RB": entry["DKPt Against RB"]}

    # Add QB, WR, and TE data
    for data, pos in [(qb_data, "DKPt Against QB"), (wr_data, "DKPt Against WR"), (te_data, "DKPt Against TE")]:
        for entry in data:
            team = entry["Team"]
            if team in merged_data:
                merged_data[team][pos] = entry[pos]
            else:
                merged_data[team] = {"Team": team, pos: entry[pos]}

    return list(merged_data.values())

def excel_maker():

    #Make dataFrames
    df_qb = make_qb_sheet()
    df_team = make_full_team_sheet()
    
    df_wr = make_wr_sheet()
    df_rb = make_rb_sheet()


    #Make excel sheet
    with pd.ExcelWriter("nfl_stats_2023.xlsx", engine="xlsxwriter") as writer:
        # Write each DataFrame to a different sheet/tab
        df_team.to_excel(writer, sheet_name="Team Stats", index=False)
        df_qb.to_excel(writer, sheet_name="QB Stats", index=False)
        df_wr.to_excel(writer, sheet_name="WR TE Stats", index=False)
        df_rb.to_excel(writer, sheet_name="RB Stats", index=False)

def find_matchups():

    schedule_file = "nfl-2024-UTC.xlsx"
    schedule = pd.read_excel(schedule_file)
    
    full_to_shorthand = {v: k for k, v in team_shorthand_to_full.items()}

    # Assuming 'Home Team' and 'Away Team' columns contain the full team names
    schedule['Home Team Shorthand'] = schedule['Home Team'].map(full_to_shorthand)
    schedule['Away Team Shorthand'] = schedule['Away Team'].map(full_to_shorthand)


    current_date = datetime.now().strftime('%Y-%m-%d')
    current_round = get_round_by_date(current_date)

  
    games_for_cur_round = schedule[schedule['Round Number'] == current_round]

    return games_for_cur_round

def get_round_by_date(date_str):
    input_date = datetime.strptime(date_str, '%Y-%m-%d')
    for round_num, (start_date_str, end_date_str) in round_to_date.items():
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        if start_date <= input_date <= end_date:
            return round_num
    return None


if __name__ == "__main__":
   #main()
   excel_maker()
   #make_team_sheet()

   
