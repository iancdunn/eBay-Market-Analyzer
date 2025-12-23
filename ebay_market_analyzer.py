from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import urllib.parse

def create_url(search_term):
    """
    Creates and returns a string containing a formatted URL targetting eBay's 'Sold & Completed' listings
    """
    base_url = "https://www.ebay.com/sch/i.html"

    params = {
        '_nkw': search_term,
        '_sacat': '0',
        '_from': 'R40',
        'rt': 'nc',
        'LH_Complete': '1',
        'LH_Sold': '1'
    }

    query = urllib.parse.urlencode(params, quote_via = urllib.parse.quote_plus)

    return f"{base_url}?{query}"


def scrape_items(search_term):
    """
    Extracts raw pricing and date data from eBay HTML
    Returns a list of dictionaries containing raw price and date strings
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)
    url = create_url(search_term)

    driver.get(url)
    
    #Waits for results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".su-card-container"))
    )

    scraped_items = driver.find_elements(By.CSS_SELECTOR, ".su-card-container")
    items = []
    for item in scraped_items:
        item_data = {}
        try:
            price_elem = item.find_element(By.CSS_SELECTOR, ".s-card__price")

            #Avoids hidden templates that match the selector but contain no data
            price_txt = price_elem.text.strip()
            if not price_txt:
                continue
            item_data['price'] = price_txt

            #Locates the date using a multi-selector strategy to handle eBay's variable view layouts
            date_elem = item.find_element(By.CSS_SELECTOR, ".s-card__caption, .su-card-container__header")
            item_data['date'] = date_elem.text
        except:

            continue

        items.append(item_data)

    driver.quit()
    return items


def clean_data(data):
    """
    Transforms raw data into a clean DataFrame with float prices and datetime objects
    """
    df = pd.DataFrame(data)
    df = df.rename(columns = {'price': 'Raw Price', 'date': 'Raw Date'})

    #Cleans price
    df['Price'] = df['Raw Price'].astype(str).str.replace(r'[$,]', '', regex = True)
    df['Price'] = pd.to_numeric(df['Price'], errors = 'coerce')
    #Parses date
    date_format = r'Sold\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})'
    df['Date Sold'] = df['Raw Date'].astype(str).str.extract(date_format, expand = False)
    df['Date Sold'] = pd.to_datetime(df['Date Sold'], errors = 'coerce')

    df = df.dropna(subset = ['Price', 'Date Sold'])
    df = df.drop(['Raw Price', 'Raw Date'], axis = 1)

    #Calculates IQR to identify and filter price outliers, removing likely irrelevant listings
    Q1 = df['Price'].quantile(0.25)
    Q3 = df['Price'].quantile(0.75)
    IQR = Q3 - Q1
    l_bound = Q1 - 1.5 * IQR
    u_bound = Q3 + 1.5 * IQR
    clean_df = df[(df['Price'] >= l_bound) & (df['Price'] <= u_bound)]

    clean_df = clean_df.sort_values(by = 'Date Sold', ascending = False)
    return clean_df

if __name__ == "__main__":
    user_input = input("Enter item to search on eBay: ")

    #ETL process execution
    raw_data = scrape_items(user_input)
    clean_df = clean_data(raw_data)

    count = len(clean_df)
    avg = clean_df['Price'].mean()
    min_price = clean_df['Price'].min()
    max_price = clean_df['Price'].max()

    print("\n" + "=" * 30)
    print(f"MARKET REPORT: {user_input.upper()}\n")
    print(f"Items Analyzed: {count}")
    print(f"Average Price: ${avg:,.2f}")
    print(f"Minimum Price: ${min_price:,.2f}")
    print(f"Maximum Price: ${max_price:,.2f}")
    print("=" * 30)


    clean_df.to_csv("item_sales.csv", index = False)
