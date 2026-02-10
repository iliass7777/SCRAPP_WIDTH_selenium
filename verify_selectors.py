import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def verify():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    print("Initializing driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://flormar.ma/categorie/teint"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(10)
        
        # Check for Load More button
        print("Checking for buttons...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons.")
        for b in buttons:
            try:
                txt = b.text.lower()
                if any(kw in txt for kw in ["voir", "plus", "load", "more"]):
                    print(f"Potential load more button: '{b.text}' (Class: {b.get_attribute('class')})")
            except:
                continue
        
        # Check for links that might be pagination
        print("Checking for potential pagination links...")
        links = driver.find_elements(By.TAG_NAME, "a")
        for l in links:
            try:
                txt = l.text.lower()
                if any(kw in txt for kw in ["voir", "plus", "load", "more", "suivant", "next"]):
                     print(f"Potential pagination link: '{l.text}' (Class: {l.get_attribute('class')}, Href: {l.get_attribute('href')})")
            except:
                continue

        # Check product count
        products = driver.find_elements(By.CSS_SELECTOR, ".Product")
        print(f"Current product count: {len(products)}")
        
        # Try a simple scroll to see if it triggers anything
        print("Attempting scroll to trigger infinite load...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        products = driver.find_elements(By.CSS_SELECTOR, ".Product")
        print(f"Product count after scroll: {len(products)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    verify()
