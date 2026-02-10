import pandas as pd
import json
import os

def convert_json_to_excel(json_file='products.json', excel_file='products.xlsx'):
    """
    Converts product JSON data to Excel format with specific columns.
    """
    try:
        print(f"Reading {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        products = data.get("products", [])
        if not products:
            print("No products found in JSON.")
            return

        # Create DataFrame
        df = pd.DataFrame(products)
        # Define the target columns and rename
        column_mapping = {
            'name': 'Nom produit',
            'category': 'Category',
            'regular_price': 'Prix',
            'has_promo': 'Promotion (oui/non)',
            'url': 'Url'
        }

        # Select and rename columns
        df_excel = df[list(column_mapping.keys())].rename(columns=column_mapping)

        # Convert boolean has_promo to "oui"/"non"
        df_excel['Promotion (oui/non)'] = df_excel['Promotion (oui/non)'].map({True: 'oui', False: 'non'})

        # Save to Excel
        print(f"Saving to {excel_file}...")
        df_excel.to_excel(excel_file, index=False)
        
        print(f"Success! {len(df_excel)} products saved to {excel_file}")

    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    convert_json_to_excel()
