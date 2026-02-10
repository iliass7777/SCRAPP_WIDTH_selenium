import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def inspect_pagination():
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
        
        # Scroll to the bottom of the 22nd product
        products = driver.find_elements(By.CSS_SELECTOR, ".Product")
        if products:
            last_p = products[-1]
            driver.execute_script("arguments[0].scrollIntoView();", last_p)
            print("Scrolled to last product.")
            time.sleep(5)
            # Now list elements right after the product list
            # We can use execute_script to find what's below the list
            print("Inspecting elements below product list...")
            # Let's save the HTML of the area around the last product
            area_html = driver.execute_script("return arguments[0].parentElement.innerHTML;", last_p)
            with open("area_snippet.html", "w", encoding="utf-8") as f:
                f.write(area_html)
            
            # Also look for any visible text that might be pagination
            all_text = driver.execute_script("return document.body.innerText;")
            if "voir" in all_text.lower() or "plus" in all_text.lower() or "load" in all_text.lower():
                print("Found pagination keywords in page text.")
            
            # Check for specific classes like 'pagination', 'load-more', etc.
            potential_classes = ["pagination", "load-more", "next", "suivant", "nav-links", "page-numbers"]
            for cls in potential_classes:
                found = driver.find_elements(By.CLASS_NAME, cls)
                if found:
                    print(f"Found element(s) with class '{cls}'")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_pagination()
