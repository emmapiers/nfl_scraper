import requests 
import pickle
from bs4 import BeautifulSoup as bs

url = "https://www.nfl.com/stats/player-stats/"



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
    base_url = 'https://www.nfl.com/stats/player-stats/category/passing/2023/REG/all/passingyards/DESC'

    all_data = []
    url = base_url
    while url:
        page_data = scrape_page(url)
        all_data.extend(page_data)
        url = get_next_page(url)

    with open('all_data.pkl', 'wb') as file:
        pickle.dump(all_data, file)
    

if __name__ == "__main__":
   main()