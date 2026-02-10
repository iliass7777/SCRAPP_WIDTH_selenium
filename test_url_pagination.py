import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_url_pagination():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Test ?page=2
        url = "https://flormar.ma/categorie/teint?page=2"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(10)
        
        products = driver.find_elements(By.CSS_SELECTOR, ".Product")
        print(f"Product count on {url}: {len(products)}")
        if len(products) > 0:
            print(f"First product on page 2: {products[0].text.split('\\n')[0]}")
            
        # Test ?p=2 as fallback
        url_p = "https://flormar.ma/categorie/teint?p=2"
        print(f"Loading {url_p}...")
        driver.get(url_p)
        time.sleep(10)
        
        products_p = driver.find_elements(By.CSS_SELECTOR, ".Product")
        print(f"Product count on {url_p}: {len(products_p)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_url_pagination()
