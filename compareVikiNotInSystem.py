from extract_rules import WikiRulesExtractor
import re
import os
import requests
import pandas as pd
import Levenshtein

def extract_all_rules():
    """Example of basic usage - extracting and iterating over anchor texts."""
    print("=== Basic Usage Example ===")
    
    # Initialize the extractor
    url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
    extractor = WikiRulesExtractor(url)
    
    # Extract law-related anchor texts
    print("Extracting law-related anchor texts...")
    law_texts = extractor.extract_all_rules(filter_laws=True)
    
    print(f"\nExtracted {len(law_texts)} law-related texts")
    print("\nFirst 5 examples:")
    for i, text in enumerate(law_texts[:5], 1):
        print(f"  {i}. {text}")
    
    return law_texts

def main():

    law_texts = extract_all_rules()
    
    # Clean each item in law_texts to remove non-alphanumeric characters
    cleaned_law_texts = []
    for text in law_texts:
        text=re.sub(r'\(\s*החדשות\s*\)', '', text)
        cleaned_law_texts.append(text.strip())

    # Fetch the content from the URL
    response = requests.get('https://www.lawdata.co.il/lawdata_face_lift_test/getallrulesnamesforcompare.asp')
    response.encoding = 'utf-8'  # Ensure proper Hebrew encoding
    
    # Split the content by *&* and store in array
    system_rules = response.text.split('*&*')
    
    # Clean each item in system_rules to remove non-alphanumeric characters
    cleaned_system_rules = []

    for text in system_rules:

#        text=re.sub(r'[\[(]נוסח [^\])]*[\])]', '', text)
 #       text = re.sub(r'[^\(\)[\]\{\}a-zA-Zא-ת0-9]*[ה]?תש([\'"״”]+|.[\'"״”]+)[^\(\)]+\d+[^\(\)[\]\{\}a-zA-Zא-ת0-9]*$', '', text)

        cleaned_system_rules.append(text.strip())

    # Find rules in viki that are NOT in system_rules
    missing_rules = []
        
    for i, viki_rule in enumerate(cleaned_law_texts):
        found = False
        
        for j, system_rule in enumerate(cleaned_system_rules):
            if "*^*" in system_rule:
                distance = Levenshtein.distance(re.sub(r'[^a-zA-Zא-ת0-9]', '', system_rule.split("*^*")[2]), re.sub(r'[^a-zA-Zא-ת0-9]', '', viki_rule))
                if (distance < 3 and len(system_rule.split("*^*")[2]) > 20) or (distance < 2 and len(system_rule.split("*^*")[2]) > 5):  # Only consider strings longer than 5 characters
                    found = True
                    break
        
        # If not found in system rules, add to missing_rules
        if not found:
            missing_rules.append(viki_rule)
    
    # Create DataFrame with missing rules
    df = pd.DataFrame(missing_rules, columns=['Rule Name'])
    
    # Save to Excel file in same directory as this py file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "vikiRulesNotInSystem.xlsx")
    df.to_excel(out_path, index=False)

    print(f"✓ Finished. Found {len(missing_rules)} rules in viki that are not in system rules.")
    print(f"✓ Saved to {out_path}")

if __name__ == "__main__":
    main()

