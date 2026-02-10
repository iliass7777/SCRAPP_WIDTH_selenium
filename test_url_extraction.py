
import json
from flormar_scraper import FlormarScraper

def test_url_extraction():
    scraper = FlormarScraper()
    # Only scrape one category for testing
    scraper.categories = {"Teint": "https://flormar.ma/categorie/teint"}
    
    # Override run to stop after first page
    original_extract = scraper.extract_from_category
    def limited_extract(name, url):
        scraper.setup_driver()
        scraper.driver.get(url)
        import time
        time.sleep(5)
        
        elements = scraper.driver.find_elements("css selector", ".Product")
        print(f"Found {len(elements)} products")
        for el in elements[:5]: # Just test first 5
            name = el.find_element("tag name", "h3").text.strip()
            anchor = el.find_element("tag name", "a")
            url = anchor.get_attribute("href")
            print(f"Product: {name}")
            print(f"URL: {url}")
        scraper.driver.quit()

    limited_extract("Teint", "https://flormar.ma/categorie/teint")

if __name__ == "__main__":
    test_url_extraction()
