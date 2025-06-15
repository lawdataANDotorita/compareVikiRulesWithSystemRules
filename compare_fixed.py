from extract_rules import WikiRulesExtractor
import re
import requests
import pandas as pd

def normalize_text(text):
    """Normalize text for comparison by removing extra spaces and some punctuation but keeping structure."""
    # Remove only specific punctuation that might vary
    text = re.sub(r'["\'\(\)\[\]\{\}]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Convert to lowercase for comparison
    return text.lower()

def extract_all_rules():
    """Extract law-related anchor texts from WikiSource."""
    print("=== Extracting Wiki Rules ===")
    
    # Initialize the extractor
    url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
    extractor = WikiRulesExtractor(url)
    
    # Extract law-related anchor texts (now with proper filtering)
    print("Extracting law-related anchor texts...")
    law_texts = extractor.extract_all_rules(filter_laws=True)
    
    print(f"\nExtracted {len(law_texts)} law-related texts")
    print("\nFirst 10 examples:")
    for i, text in enumerate(law_texts[:10], 1):
        print(f"  {i}. {text}")
    
    return law_texts

def main():
    # Extract law texts from wiki
    law_texts = extract_all_rules()
    
    # Fetch system rules
    print("\n=== Fetching System Rules ===")
    response = requests.get('https://www.lawdata.co.il/getallhoknamesforcompare.asp')
    response.encoding = 'utf-8'
    system_rules = response.text.split('*&*')
    
    print(f"Got {len(system_rules)} system rules")
    print("\nFirst 5 system rules:")
    for i, text in enumerate(system_rules[:5], 1):
        print(f"  {i}. {text}")
    
    # Normalize both datasets for comparison
    print("\n=== Normalizing Data ===")
    normalized_law_texts = [normalize_text(text) for text in law_texts]
    normalized_system_rules = [normalize_text(text) for text in system_rules]
    
    # Remove empty entries
    normalized_law_texts = [text for text in normalized_law_texts if text.strip()]
    valid_system_rules = [(original, normalized) for original, normalized in zip(system_rules, normalized_system_rules) if normalized.strip()]
    
    print(f"After normalization and filtering:")
    print(f"  Wiki law texts: {len(normalized_law_texts)}")
    print(f"  System rules: {len(valid_system_rules)}")
    
    # Find matches and missing rules
    print("\n=== Finding Matches ===")
    missing_rules = []
    matches_found = 0
    
    for original_rule, normalized_rule in valid_system_rules:
        if normalized_rule in normalized_law_texts:
            matches_found += 1
            if matches_found <= 5:  # Show first 5 matches
                print(f"MATCH: {original_rule}")
        else:
            missing_rules.append(original_rule)
    
    # Results
    print(f"\n=== Results ===")
    print(f"Total system rules: {len(valid_system_rules)}")
    print(f"Matches found: {matches_found}")
    print(f"Missing rules: {len(missing_rules)}")
    print(f"Match percentage: {matches_found/len(valid_system_rules)*100:.1f}%")
    
    # Save missing rules to Excel
    if missing_rules:
        df = pd.DataFrame(missing_rules, columns=['Rule Name'])
        df.to_excel('missing_rules_fixed.xlsx', index=False)
        print(f"\n✓ Saved {len(missing_rules)} missing rules to 'missing_rules_fixed.xlsx'")
    else:
        print("\n✓ No missing rules found!")

if __name__ == "__main__":
    main() 