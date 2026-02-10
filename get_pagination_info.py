import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_pagination_html():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://flormar.ma/categorie/teint"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(10)
        
        # Find pagination element
        paginations = driver.find_elements(By.CSS_SELECTOR, ".pagination")
        if paginations:
            for i, p in enumerate(paginations):
                print(f"Pagination block {i} outerHTML:")
                print(p.get_attribute("outerHTML"))
        else:
            print("No element with class 'pagination' found.")
            
        # Also check for any links that look like /page/2 or ?page=2
        links = driver.find_elements(By.TAG_NAME, "a")
        for l in links:
            try:
                href = l.get_attribute("href")
                if href and ("page" in href.lower() or "p=" in href.lower()):
                    print(f"Interesting link: {l.text} -> {href}")
            except:
                continue

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_pagination_html()
