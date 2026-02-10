
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def extract():
    try:
        with open("page_source.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        target = 'class="Product"'
        index = content.find(target)
        
        if index == -1:
            print("Target not found.")
            return
            
        # Start 1000 chars after the product start
        start = index + 1000
        end = min(len(content), start + 1500)
        
        snippet = content[start:end]
        print(f"--- SNIPPET START ---\n{snippet}\n--- SNIPPET END ---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract()
