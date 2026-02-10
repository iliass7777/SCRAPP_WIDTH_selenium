
import json
import time
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

class FlormarScraper:
    def __init__(self):
        self.base_url = "https://flormar.ma"
        self.products = []
        self.seen_products = set()
        
        # Categories to scrape
        self.categories = {
            "Teint": "https://flormar.ma/categorie/teint",
            "Yeux": "https://flormar.ma/categorie/yeux",
            "Lèvres": "https://flormar.ma/categorie/lips",
            "Ongles": "https://flormar.ma/categorie/ongles",
            "Soins": "https://flormar.ma/categorie/skin-care",
            "Accessoires": "https://flormar.ma/categorie/accessoires",
            "Vegan": "https://flormar.ma/categorie/vegan",
            "Flormar Deals": "https://flormar.ma/categorie/flormar-deals"
        }
        # Reduced category list for faster feedback during dev/debug

    def setup_driver(self):
        print("Setting up driver...", flush=True)
        options = Options()
        options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        print("Driver initialized.", flush=True)

    def scroll_to_bottom(self):
        print("  Scrolling to load all products...", flush=True)
        
        # Initial wait
        time.sleep(2)
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        products_count = 0
        
        no_change_count = 0
        max_no_change = 3 # Stop after 3 attempts with no new products
        
        while True:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Also try scrolling up a bit and back down to trigger potential lazy load events
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 300);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Check new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Check product count
            current_products = self.driver.find_elements(By.CSS_SELECTOR, ".Product, .type-product")
            current_count = len(current_products)
            
            print(f"  ... loaded {current_count} items so far", flush=True)

            if current_count > products_count:
                products_count = current_count
                no_change_count = 0 # Reset if we found new products
            else:
                if new_height == last_height:
                    no_change_count += 1
                    if no_change_count >= max_no_change:
                        print("  No new products loaded after multiple attempts. Stopping scroll.", flush=True)
                        break
                else:
                    no_change_count = 0 # Reset if height changed but maybe products not rendered yet
    def extract_from_category(self, category_name, url):
        print(f"Scraping category: {category_name} ({url})", flush=True)
        self.driver.get(url)
        time.sleep(5)
        
        page_num = 1
        
        while True:
            print(f"  Scraping page {page_num}...", flush=True)
            # Wait for products to be visible
            try:
                # Scroll to ensure elements are loaded (if lazy loading within page)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                elements = self.driver.find_elements(By.CSS_SELECTOR, ".Product")
                print(f"  Found {len(elements)} products on this page", flush=True)
                
                for el in elements:
                    try:
                        name_el = el.find_element(By.TAG_NAME, "h3")
                        name = name_el.text.strip()
                        
                        if not name:
                            continue

                        # URL extraction
                        product_url = "N/A"
                        try:
                            # The product URL is usually in the first <a> tag
                            anchor = el.find_element(By.TAG_NAME, "a")
                            href = anchor.get_attribute("href")
                            if href:
                                product_url = href
                        except:
                            pass

                        product_key = (name + category_name).lower()
                        if product_key in self.seen_products:
                            continue
                        self.seen_products.add(product_key)

                        # Price extraction
                        reg_price = "N/A"
                        promo_price = None
                        has_promo = False

                        try:
                            # Check for sale price structure: <del>Original</del> <ins>Current</ins>
                            # OR <span class="price"><ins>...</ins><del>...</del></span>
                            
                            # We look for the general price container first to scope our search
                            price_container = el
                            try:
                                price_container = el.find_element(By.CSS_SELECTOR, ".price")
                            except:
                                pass

                            # Check for discount
                            ins_elements = price_container.find_elements(By.TAG_NAME, "ins")
                            del_elements = price_container.find_elements(By.TAG_NAME, "del")

                            if ins_elements and del_elements:
                                reg_price = ins_elements[0].text.strip()
                                promo_price = del_elements[0].text.strip()
                                has_promo = True
                            else:
                                # Regular price
                                # Try to find the amount directly
                                amount_elements = price_container.find_elements(By.CSS_SELECTOR, ".woocommerce-Price-amount")
                                if amount_elements:
                                    reg_price = amount_elements[0].text.strip()
                                else:
                                    # Fallback to text analysis if structured elements fail
                                    text = price_container.text
                                    import re
                                    matches = re.findall(r'(\d+[.,]\d+\s*(?:Dh|MAD))', text)
                                    if matches:
                                        reg_price = matches[0]
                                        if len(matches) > 1:
                                            # If two prices found in text but no del/ins tags, likely sale
                                            # Usually lower is better/current
                                            pass 
                        except Exception as e:
                            # print(f"Price extraction error: {e}")
                            pass
                        
                        item = {
                            "name": name,
                            "category": category_name,
                            "url": product_url,
                            "regular_price": reg_price,
                            "promotional_price": promo_price,
                            "has_promo": has_promo
                        }
                        
                        self.products.append(item)
                            
                    except Exception as e:
                        # print(f"    Error extracting individual product: {e}")
                        continue
                
                # Check for Next Button
                # The "Next" button is the last button in .pagination
                pagination = self.driver.find_elements(By.CSS_SELECTOR, ".pagination")
                if not pagination:
                    print("  No pagination found.", flush=True)
                    break
                    
                buttons = pagination[0].find_elements(By.TAG_NAME, "button")
                if not buttons:
                    break
                    
                next_button = buttons[-1] # The chevron-right button
                
                # Check if it has a chevron-right or is just the last button
                # The first and last buttons are usually arrows
                # The first is disabled on page 1
                
                is_disabled = next_button.get_attribute("disabled") is not None
                if is_disabled:
                    print("  Reach last page.", flush=True)
                    break
                
                # Check if it has the chevron-right icon
                svg = next_button.find_elements(By.TAG_NAME, "svg")
                if not svg:
                    # If the last button isn't an arrow, maybe no next page
                    break
                
                print(f"  Clicking next page...", flush=True)
                
                # Store current first product name to detect page change
                first_name = self.products[-1]["name"] if self.products else "" # Check last added product
                
                # Click next
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
                
                # Verify page changed
                new_elements = self.driver.find_elements(By.CSS_SELECTOR, ".Product")
                if new_elements:
                    new_first_name = new_elements[0].find_element(By.TAG_NAME, "h3").text.strip()
                    if new_first_name == first_name:
                         # Page didn't change?
                         print("  Page content didn't change after click. stopping.", flush=True)
                         break
                
                page_num += 1
                
            except Exception as e:
                print(f"  Error in pagination loop: {e}", flush=True)
                break
        
        print(f"  Finished category {category_name}. Total: {len(self.products)} products.", flush=True)

        # Save intermediate results
        self.save_json()


    def save_json(self, filename="products.json"):
        data = {
            "scraping_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_products": len(self.products),
            "products": self.products
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.products)} products to {filename}", flush=True)

    def run(self):
        try:
            self.setup_driver()
            
            for cat_name, url in self.categories.items():
                try:
                    self.extract_from_category(cat_name, url)
                except Exception as e:
                    print(f"Error scraping category {cat_name}: {e}", flush=True)
            
        except Exception as e:
            print(f"Critical Error: {e}", flush=True)
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

if __name__ == "__main__":
    scraper = FlormarScraper()
    scraper.run()
