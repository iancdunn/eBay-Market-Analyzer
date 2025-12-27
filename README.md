# eBay Market Analyzer

![Nintendo 3DS Dashboard](Nintendo 3DS Sales Report.pdf)

A Python-based ETL tool that scrapes "Sold & Completed" listings from eBay to generate accurate market pricing reports. It automates data extraction using Selenium, performs rigorous data cleaning with Pandas, and filters outliers using Interquartile Range (IQR) logic to ensure statistical accuracy.

## Features

* **Automated Extraction:** Uses `Selenium` in headless mode to scrape listing prices and sale dates.
* **Robust Selectors:** Implements multi-selector strategies to handle eBay's variable frontend layouts (e.g., handling different list view types).
* **ETL Pipeline:**
    * **Extract:** Scrapes raw HTML elements.
    * **Transform:** Cleans currency strings, parses irregular date formats using Regex, and casts data types.
    * **Load:** Exports structured data to CSV and prints a summary report.
* **Statistical Filtering:** Automatically removes pricing outliers (irrelevant accessories or bulk mis-listings) using IQR (Interquartile Range) calculation to prevent skewed averages.
* **Driver Management:** Utilizes `webdriver_manager` to automatically handle Chrome driver versions.

## Prerequisites

* Python 3.x
* Google Chrome installed on the local machine.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/iancdunn/eBay-Market-Analyzer.git
    cd eBay-Market-Analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install pandas selenium webdriver-manager
    ```

## Usage

1.  Run the script:
    ```bash
    python ebay_market_analyzer.py
    ```

2.  Enter the item name when prompted (e.g., `Sony WH-1000XM4`).

3.  The script will:
    * Launch a headless Chrome browser.
    * Scrape relevant sold listings.
    * Clean the data and remove outliers.
    * Print a **Market Report** to the console.
    * Save the detailed dataset to `item_sales.csv`.

### Example Output

**Console:**
```text
==============================
MARKET REPORT: SONY WH-1000XM4

Items Analyzed: 45
Average Price: $185.50
Minimum Price: $120.00
Maximum Price: $230.00
==============================
```

**CSV Output (`item_sales.csv`):**
| Price | Date Sold |
|-------|-----------|
| 185.00| 2023-10-25|
| 190.50| 2023-10-24|
| ...   | ...       |

## Logic Breakdown

* **`scrape_items(search_term)`**: Handles the browser interaction. It waits for the DOM to load (`EC.presence_of_all_elements_located`) to ensure dynamic content is captured before scraping.
* **`clean_data(data)`**: The core transformation layer.
    * Converts raw strings (e.g., "$1,200.00") into floats.
    * Extracts dates from strings like "Sold Oct 12, 2023" into standard Datetime objects.
    * **Outlier Logic**: Calculates `Q1` and `Q3` to determine the IQR. Any price falling outside `1.5 * IQR` is dropped.
