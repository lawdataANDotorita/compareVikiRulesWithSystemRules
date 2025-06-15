#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract all anchor tag text content from Hebrew Wikisource law page.
"""

import requests
from bs4 import BeautifulSoup
from typing import List
import time
import re


class WikiRulesExtractor:
    """Extract rules/laws from Hebrew Wikisource page."""
    
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        # Add headers to mimic a browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_page_content(self) -> str:
        """Fetch the HTML content of the page."""
        try:
            print(f"Fetching content from: {self.url}")
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Ensure proper Hebrew encoding
            print(f"Successfully fetched page. Status code: {response.status_code}")
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            raise
    
    def extract_anchor_texts(self, html_content: str) -> List[str]:
        """Extract all text content from anchor tags."""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Find all anchor tags
        anchor_tags = soup.find_all('a')
        
        # Extract text content from each anchor tag
        anchor_texts = []
        for tag in anchor_tags:
            text = tag.get_text(strip=True)
            if text:  # Only include non-empty text
                anchor_texts.append(text)
        
        print(f"Found {len(anchor_texts)} anchor tags with text content")
        return anchor_texts
    
    def filter_law_related_links(self, anchor_texts: List[str]) -> List[str]:
        """Filter anchor texts to get law-related content."""
        # Keywords that indicate law-related content in Hebrew
        law_keywords = [
            'חוק', 'תקנות', 'פקודה', 'צו', 'הוראה', 'חוקה', 'תחיקה',
            'משפט', 'פקודת', 'חוקי', 'תקנת', 'הלכה', 'דין'
        ]
        
        # Navigation and non-law elements to exclude
        exclude_keywords = [
            'לדלג', 'עמוד ראשי', 'ברוכים הבאים', 'שינויים אחרונים', 
            'דף אקראי', 'שער הקהילה', 'עזרה', 'מזנון', 'ארגז חול',
            'בקשות מבעלי הרשאות', 'צור קשר', 'יציאה', 'שפה', 'דפדוף',
            'הדפסה', 'מידע', 'תרומה', 'קישור', 'עריכה', 'היסטוריה',
            'דיון', 'קטגוריה', 'תבנית', 'נושא', 'נושאים', 'רשימה'
        ]
        
        filtered_texts = []

        for text in anchor_texts:
            # Skip if it's a navigation element
            if any(exclude_word in text for exclude_word in exclude_keywords):
                continue
                
            # Include if it contains law-related keywords
            if any(keyword in text for keyword in law_keywords):
                filtered_texts.append(text)
            
            # Also include if it looks like a year pattern (law format)
            if re.search(r'התש[נסעפצקרש]"[א-ת]-\d{4}', text):
                filtered_texts.append(text)

        print(f"Filtered to {len(filtered_texts)} law-related anchor texts")
        return filtered_texts
    
    def extract_all_rules(self, filter_laws: bool = True) -> List[str]:
        """Main method to extract all rules/laws from the page."""
        try:
            # Fetch page content
            html_content = self.fetch_page_content()
            
            # Extract all anchor texts
            anchor_texts = self.extract_anchor_texts(html_content)
            
            if filter_laws:
                # Filter to get only law-related content
                rules_vector = self.filter_law_related_links(anchor_texts)
            else:
                rules_vector = anchor_texts
            
            return rules_vector
            
        except Exception as e:
            print(f"Error extracting rules: {e}")
            raise


def main():
    """Main function to demonstrate the extractor."""
    url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
    
    print("Starting Hebrew Wiki Rules Extractor...")
    print("=" * 50)
    
    # Create extractor instance
    extractor = WikiRulesExtractor(url)
    
    # Extract all anchor texts (unfiltered)
    print("\n1. Extracting ALL anchor tag texts:")
    all_anchor_texts = extractor.extract_all_rules(filter_laws=False)
    
    print(f"\nFirst 10 anchor texts (out of {len(all_anchor_texts)}):")
    for i, text in enumerate(all_anchor_texts[:10], 1):
        print(f"  {i}. {text}")
    
    # Extract filtered law-related texts
    print("\n" + "=" * 50)
    print("\n2. Extracting FILTERED law-related anchor texts:")
    law_related_texts = extractor.extract_all_rules(filter_laws=True)
    
    print(f"\nFirst 20 law-related texts (out of {len(law_related_texts)}):")
    for i, text in enumerate(law_related_texts[:20], 1):
        print(f"  {i}. {text}")
    
    # Save results to file
    print("\n" + "=" * 50)
    print("\n3. Saving results to files...")
    
    # Save all anchor texts
    with open('all_anchor_texts.txt', 'w', encoding='utf-8') as f:
        for i, text in enumerate(all_anchor_texts, 1):
            f.write(f"{i}. {text}\n")
    
    # Save filtered law texts
    with open('law_related_texts.txt', 'w', encoding='utf-8') as f:
        for i, text in enumerate(law_related_texts, 1):
            f.write(f"{i}. {text}\n")
    
    print(f"✓ Saved {len(all_anchor_texts)} anchor texts to 'all_anchor_texts.txt'")
    print(f"✓ Saved {len(law_related_texts)} law-related texts to 'law_related_texts.txt'")
    
    # Return the vectors for further use
    return all_anchor_texts, law_related_texts


if __name__ == "__main__":
    try:
        all_texts, law_texts = main()
        print("\n" + "=" * 50)
        print("✓ Extraction completed successfully!")
        print(f"✓ You can now iterate over {len(all_texts)} total anchor texts")
        print(f"✓ Or iterate over {len(law_texts)} filtered law-related texts")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your internet connection and try again.") 