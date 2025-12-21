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
    response = requests.get('https://www.lawdata.co.il/lawdata_face_lift_test/getallhoknamesforcompare.asp')
    response.encoding = 'utf-8'  # Ensure proper Hebrew encoding
    
    # Split the content by *&* and store in array
    system_rules = response.text.split('*&*')
    
    # Clean each item in system_rules to remove non-alphanumeric characters
    cleaned_system_rules = []
    rules_variations=[]

    for text in system_rules:
        textOrg = text
        text2=text

        text=re.sub(r'[\[(]נוסח [^\])]*[\])]', '', text)
        text = re.sub( r'[^\(\)[\]\{\}a-zA-Zא-ת0-9]*[א-ת"׳]+\s*([-–]\s*)?\d{2,6}[^\(\)[\]\{\}a-zA-Zא-ת0-9]*$', '', text)

        # text2 = re.sub( r'[^a-zA-Zא-ת0-9]*\s*([-–]\s*)?\d{2,6}[^a-zA-Zא-ת0-9]*$', '', text2)
        #  text2=re.sub(r'[\[(]נוסח [^\])]*[\])]', '', text2)

        text2=re.sub(r'[\[(]נוסח [^\])]*[\])]', '', text2)
        text2 = re.sub(r'[^\(\)[\]\{\}a-zA-Zא-ת0-9]*[ה]?תש([\'"״”]+|.[\'"״”]+)[^\(\)]+\d+[^\(\)[\]\{\}a-zA-Zא-ת0-9]*$', '', text2)
        text2 = re.sub(r',\s*\d{4}$', '', text2)

        cleaned_system_rules.append(text2.strip())
        if text != text2 :
            rules_variations.append({
                'textOrg': textOrg,
                'text': text,
                'text2': text2
            })

    
    if rules_variations:
        # Save cleaned_system_rules to Excel in same directory as this py file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(script_dir, "systemRulesWithSpecialSuffix.xlsx")
        # Save rules_variations (with columns textOrg, text, text2) to Excel
        df_rules_variations = pd.DataFrame(rules_variations, columns=['textOrg', 'text', 'text2'])
        df_rules_variations.to_excel(out_path, index=False)
    
    
    # Find rules in system_rules that are not in law_texts
    existing_rules = []
        
    for i,viki_rule in enumerate(cleaned_law_texts):
        if "פיצוי וסיוע בשל ביטול טיסה" in viki_rule: #for debugging
            m=1
        for j,system_rule in enumerate(cleaned_system_rules):
            if "פיצוי וסיוע בשל ביטול טיסה" in system_rule: #for debugging
                m=2

            if "*^*" in system_rule:
                distance = Levenshtein.distance(re.sub(r'[^a-zA-Zא-ת0-9]', '', system_rule.split("*^*")[1]), re.sub(r'[^a-zA-Zא-ת0-9]', '', viki_rule))
                if (distance < 3 and len(system_rule.split("*^*")[1]) > 20) or (distance < 2 and len(system_rule.split("*^*")[1]) > 5 ):  # Only consider strings longer than 5 characters
                    rule_c_and_name = system_rule.split("*^*")[0]+"*&*"+viki_rule
                    existing_rules.append(rule_c_and_name)
                    break
    
    # Create DataFrame with existing rules

    # Split each item in existing_rules by '*&*' and create separate columns
    split_rules = [rule.split('*&*') for rule in existing_rules]
    df = pd.DataFrame(split_rules, columns=['Rule Index', 'Rule Name'])
    
    # Save to Excel file
    df.to_excel('existing_rules_181225.xlsx', index=False)

    print (f"✓ finished")

if __name__ == "__main__":
    main() 