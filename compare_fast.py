from extract_rules import WikiRulesExtractor
import re
import requests
import pandas as pd

def simple_similarity(str1, str2, threshold=0.8):
    """Simple similarity check based on common characters."""
    if len(str1) == 0 or len(str2) == 0:
        return False
    
    # Check if shorter string is mostly contained in longer string
    shorter, longer = (str1, str2) if len(str1) <= len(str2) else (str2, str1)
    
    if len(shorter) < 5:  # Skip very short strings
        return False
    
    # Count matching characters in order
    matches = 0
    j = 0
    for i, char in enumerate(shorter):
        while j < len(longer) and longer[j] != char:
            j += 1
        if j < len(longer):
            matches += 1
            j += 1
    
    similarity = matches / len(shorter)
    return similarity >= threshold

def extract_all_rules():
    """Extract law-related anchor texts from WikiSource."""
    print("=== Extracting Wiki Rules ===")
    
    url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
    extractor = WikiRulesExtractor(url)
    
    print("Extracting law-related anchor texts...")
    law_texts = extractor.extract_all_rules(filter_laws=True)
    
    print(f"\nExtracted {len(law_texts)} law-related texts")
    print("\nFirst 5 examples:")
    for i, text in enumerate(law_texts[:5], 1):
        print(f"  {i}. {text}")
    
    return law_texts

def main():
    law_texts = extract_all_rules()
    
    # Clean law texts
    cleaned_law_texts = []
    for text in law_texts:
        cleaned_text = re.sub(r'[^a-zA-Zא-ת0-9]', '', text)
        cleaned_law_texts.append(cleaned_text)

    # Fetch system rules
    print("\n=== Fetching System Rules ===")
    response = requests.get('https://www.lawdata.co.il/lawdata_face_lift_test/getallhoknamesforcompare.asp')
    response.encoding = 'utf-8'
    system_rules = response.text.split('*&*')
    
    print(f"Got {len(system_rules)} system rules")
    
    # Clean system rules
    cleaned_system_rules = []
    for text in system_rules:
        # Remove year suffix if present
        text = text.rsplit(',', 1)[0] if ',' in text else text
        
        # Remove version text patterns
        text = re.sub(r'\[נוסח [^\]]*\]', '', text)
        
        # Clean to alphanumeric only
        cleaned_text = re.sub(r'[^a-zA-Zא-ת0-9]', '', text)
        cleaned_system_rules.append(cleaned_text)

    # Find missing rules with similarity check
    print("\n=== Finding Missing Rules (with similarity check) ===")
    missing_rules = []
    similar_found = 0
    
    for i, cleaned_rule in enumerate(cleaned_system_rules):
        if len(cleaned_rule) < 5:  # Skip very short rules
            continue
            
        # Check exact match first
        if cleaned_rule in cleaned_law_texts:
            continue
            
        # Check similarity
        is_similar = False
        for existing_rule in cleaned_law_texts:
            if simple_similarity(cleaned_rule, existing_rule):
                is_similar = True
                similar_found += 1
                break
        
        if not is_similar:
            missing_rules.append(system_rules[i])
    
    # Results
    print(f"\nResults:")
    print(f"Total system rules: {len(system_rules)}")
    print(f"Similar rules found: {similar_found}")
    print(f"Missing rules: {len(missing_rules)}")
    
    # Save to Excel
    df = pd.DataFrame(missing_rules, columns=['Rule Name'])
    df.to_excel('missing_rules_with_similarity.xlsx', index=False)
    
    print(f"✓ Saved {len(missing_rules)} missing rules to 'missing_rules_with_similarity.xlsx'")

if __name__ == "__main__":
    main() 