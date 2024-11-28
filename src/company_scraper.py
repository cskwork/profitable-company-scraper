import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_company_info(symbol):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    data = {}
    
    try:
        # Get company overview
        url = f"https://finance.yahoo.com/quote/{symbol}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get current price
        price_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
        if price_element:
            data['current_price'] = price_element.text
            
        # Get key statistics
        stats_url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics"
        response = requests.get(stats_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    data[key] = value
        
        # Get additional info from profile page
        profile_url = f"https://finance.yahoo.com/quote/{symbol}/profile"
        response = requests.get(profile_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        description = soup.find('p', {'class': 'Mt(15px) Lh(1.6)'})
        if description:
            data['company_description'] = description.text.strip()
            
        employees = soup.find('span', string='Full Time Employees')
        if employees and employees.find_next('span'):
            data['employees'] = employees.find_next('span').text
            
    except Exception as e:
        print(f"Error scraping {symbol}: {str(e)}")
    
    return data

def main():
    companies = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'NVDA': 'NVIDIA Corporation',
        'META': 'Meta Platforms'
    }
    
    all_data = {}
    for symbol, name in companies.items():
        print(f"Scraping data for {name}...")
        company_data = scrape_company_info(symbol)
        all_data[symbol] = company_data
        time.sleep(2)  # Be nice to the server
    
    # Save the data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'company_data_{timestamp}.json', 'w') as f:
        json.dump(all_data, f, indent=4)
    
    print("Data collection complete. Check the JSON file for results.")

if __name__ == "__main__":
    main()
