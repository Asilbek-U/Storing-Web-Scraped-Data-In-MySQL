import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
import mysql.connector
from urllib.parse import urljoin

start_time = time.time()

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:109.0) Gecko/20100101 Firefox/117.0"
]

options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument(f"--window-size=1920,1800")
# options.add_argument("--headless")

driver = uc.Chrome(options=options)
url = "https://quotes.toscrape.com/"

def scrape_data(url):

    driver.get(url)

    results = []

    while True:

        time.sleep(random.uniform(1.5, 3.5))

        quotes = driver.find_elements(By.CLASS_NAME, "quote")

        for quote in quotes:
            text = "N/A"
            author = "N/A"
            try:
                text = quote.find_element(By.CLASS_NAME, "text").text.strip()
                
                author = quote.find_element(By.CLASS_NAME, "author").text.strip()
                
                tags_element = quote.find_element(By.CLASS_NAME, "keywords")
                tags = tags_element.get_attribute('content')
                if not tags:
                    tags = "N/A"
            except Exception as e:
                print(f"Skipping this quote due to an error: {e}")
                continue

            results.append((text, author, tags))
        

        try:
            next_element = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            next_button = next_element.get_attribute('href')
            url = urljoin(url, next_button)
            next_element.click()
        except Exception as e:
            break

    driver.quit()
    return results

def export_data(results):
    
    conn = mysql.connector.connect(
        host = "your_host",
        user = "your_user",
        password = "your_password",
        database = "your_database"
    )

    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS quotes")

    cursor.execute("""
    CREATE TABLE quotes(
                id INT PRIMARY KEY AUTO_INCREMENT,
                quote TEXT NOT NULL,
                author VARCHAR(100) NOT NULL,
                tags VARCHAR(1000) 
    )""")

    cursor.executemany('INSERT INTO quotes (quote, author, tags) VALUES (%s, %s, %s)', results)

    conn.commit()
    cursor.close()
    conn.close()

results = scrape_data(url)

end_time = time.time()
current_time = end_time - start_time
minutes = int(current_time // 60)
seconds = int(current_time % 60)
print(f"Scraping took {minutes} minute(s) and {seconds} second(s)")

export_data(results)
