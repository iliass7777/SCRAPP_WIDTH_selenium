#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glovo Product Scraper
Simple function to scrape products from any Glovo URL
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape(url, wait_time=30):
    """
    Scrape products from a store URL
    
    Args:
        url (str):  store URL
        wait_time (int): Seconds to wait for products to load (default: 30)
    
    Returns:
        list: List of products with name, price, category, etc.
    
   
    """

    # Setup Chrome
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    products = []
    
    try:
        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Accept cookies
        try:
            time.sleep(3)
            buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]")
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(2)
                    break
        except:
            pass
        
        # Wait for products
        print(f"Waiting {wait_time}s for products...")
        time.sleep(wait_time)
        
        # Scroll
        print("Scrolling...")
        for i in range(5):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Extract category from URL
        category = "Products"
        if 'section=' in url:
            match = re.search(r'([a-z-]+)-s\.', url.split('section=')[-1])
            if match:
                category = match.group(1).replace('-', ' ').title()
        elif 'content=' in url:
            content = url.split('content=')[-1].split('&')[0]
            parts = content.split('%2F')
            last = parts[-1] if len(parts) > 1 else content
            match = re.search(r'([a-z-]+)-c\.', last)
            if match:
                category = match.group(1).replace('-', ' ').title()
        
        # Extract products
        print("Extracting products...")
        seen = set()
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'MAD')]")
        print(f"Found {len(elements)} price elements")
        
        for elem in elements:
            try:
                # Get parent context
                parent = elem
                for _ in range(3):
                    try:
                        parent = parent.find_element(By.XPATH, "..")
                    except:
                        break
                
                text = parent.text
                if not text or len(text) < 10:
                    continue
                
                # Skip non-products
                skip = ['casablanca', 'fees', 'enter your', 'prime', 'login', 'delivery', 'your order']
                if any(s in text.lower() for s in skip) and text.count('\n') < 3:
                    continue
                
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                name = None
                prices = []
                discount = None
                
                for line in lines:
                    # Find prices
                    price_matches = re.findall(r'(\d+[,\.]\d+|\d+)\s*MAD', line)
                    prices.extend([p.replace(',', '.') for p in price_matches])
                    
                    # Find discount
                    disc = re.search(r'-(\d+)%', line)
                    if disc:
                        discount = f"-{disc.group(1)}%"
                    
                    # Find name
                    if len(line) > 5 and 'MAD' not in line and not line.replace(' ', '').isdigit():
                        if not any(s in line.lower() for s in skip):
                            if not name:
                                name = line
                
                if name and prices:
                    key = name.lower().replace(' ', '')
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    product = {
                        "name": name,
                        "price": f"{prices[0]} MAD",
                        "category": category,
                        "has_promo": discount is not None,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    if len(prices) >= 2:
                        product["original_price"] = f"{prices[1]} MAD"
                    if discount:
                        product["discount"] = discount
                    
                    products.append(product)
                    
            except:
                continue
        
        print(f"Extracted {len(products)} products")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()
    
    return products


def save_json(products, filename="products.json"):
    """Save products to JSON file"""
    output = {
        "scraping_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_products": len(products),
        "products": products
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {filename}")
    return filename


# Example usage
if __name__ == "__main__":
   
    url = "https://exemples.com"
    scrape(url)
   # save_json(products)
    
  
  
