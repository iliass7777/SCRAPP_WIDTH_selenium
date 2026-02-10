import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def analyze():
    options = Options()
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load local file
        path = os.path.abspath("page_source.html")
        url = f"file:///{path}"
        print(f"Loading {url}...")
        driver.get(url)
        
        # Find product
        print("Searching for product...")
        # Try to find the specific product text
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'PRECIOUS CURL MASCARA')]")
        
        if not elements:
            print("Product not found.")
            return

        print(f"Found {len(elements)} elements with product name.")
        
        # Analyze the first one
        el = elements[0]
        print(f"Element tag: {el.tag_name}")
        print(f"Element text: {el.text}")
        
        # Go up to find the product card container
        parent = el
        for i in range(5):
            parent = parent.find_element(By.XPATH, "..")
            print(f"Parent {i+1}: {parent.tag_name} class='{parent.get_attribute('class')}' id='{parent.get_attribute('id')}'")
            
            # Check if this parent contains price
            try:
                price_els = parent.find_elements(By.XPATH, ".//*[contains(text(), 'Dhs') or contains(text(), 'MAD')]")
                if price_els:
                    print(f"  -> Contains {len(price_els)} price elements.")
                    for p in price_els:
                        print(f"     Price Text: {p.text}, Class: {p.get_attribute('class')}")
            except:
                pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze()
