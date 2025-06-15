from extract_rules import WikiRulesExtractor
import re
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
        cleaned_text = re.sub(r'[^a-zA-Zא-ת0-9]', '', text)
        cleaned_law_texts.append(cleaned_text)




    # Fetch the content from the URL
    response = requests.get('https://www.lawdata.co.il/lawdata_face_lift_test/getallhoknamesforcompare.asp')
    response.encoding = 'utf-8'  # Ensure proper Hebrew encoding
    
    # Split the content by *&* and store in array
    system_rules = response.text.split('*&*')
    
    # Clean each item in system_rules to remove non-alphanumeric characters
    cleaned_system_rules = []
    for text in system_rules:


        text = re.sub( r'\s*[,]\s*[א-ת"׳]+\s*([-–]\s*)?\d{4}\s*$', '', text)


        # The issue is that the current regex pattern is looking for ']נוסח' followed by any characters until '['
        # To catch '[נוסח משולב]', we need to modify the pattern to look for the full phrase
###        text = re.sub(r'נוסח משולב', '', text)
###        text = re.sub(r'נוסח חדש', '', text)

        text=re.sub(r'\[נוסח [^\]]*\]', '', text)





        cleaned_text = re.sub(r'[^a-zA-Zא-ת0-9]', '', text)
        cleaned_system_rules.append(cleaned_text)


    # Find rules in system_rules that are not in law_texts
    missing_rules = []
    for i, cleaned_rule in enumerate(cleaned_system_rules):
        
        # Check if the rule is similar to any existing rule using Levenshtein distance
        is_similar = False
        for existing_rule in cleaned_law_texts:
            # Calculate Levenshtein distance between the two strings
            distance = Levenshtein.distance(cleaned_rule, existing_rule)
            # If the distance is small relative to the length of the strings, consider them similar
            if distance <= 3 and len(cleaned_rule) > 5:  # Only consider strings longer than 5 characters
                is_similar = True
                break
        
        if is_similar:
            continue
        
        missing_rules.append(system_rules[i])
    
    # Print the missing rules with their original names
    
    # Create DataFrame with missing rules
    df = pd.DataFrame(missing_rules, columns=['Rule Name'])
    
    # Save to Excel file
    df.to_excel('missing_rules_main_sub_rules.xlsx', index=False)

    print (f"✓ finished")

if __name__ == "__main__":
    main() 