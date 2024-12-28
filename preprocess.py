from typing import Dict, List, Any
import json
from pathlib import Path

class DataProcessor:
    def __init__(self, scraped_data_path: Path):
        self.raw_data = self._load_data(scraped_data_path)
        
    def _load_data(self, filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_for_chatgpt(self) -> Dict[str, Any]:
        """Structure data for ChatGPT consumption"""
        return {
            "website_overview": {
                "title": self.raw_data.get('title', ''),
                "meta_description": self.raw_data.get('meta', {}).get('description', ''),
                "main_topics": self._extract_main_topics()
            },
            "content_sections": self._process_main_content(),
            "all_links": self._extract_all_links(),
            "navigation_structure": self._process_navigation(),
            "key_features": self._extract_key_features(),
            "contact_info": self._extract_contact_info(),
            "all_links": self._extract_all_links()
        }
    
    def _extract_main_topics(self) -> List[str]:
        """Extract main topics from headers and navigation"""
        topics = []
        for content in self.raw_data.get('mainContent', []):
            if content.get('tag') in ['h1', 'h2', 'h3']:
                topics.append(content.get('text', ''))
        return list(set(topics))
    
    def _process_main_content(self) -> List[Dict]:
        """Process and structure main content sections"""
        sections = []
        for content in self.raw_data.get('mainContent', []):
            section = {
                "title": self._find_section_title(content),
                "content": content.get('text', ''),
                "type": content.get('tag', ''),
                "id": content.get('id', ''),
            }
            sections.append(section)
        return sections
    
    def _process_navigation(self) -> List[Dict]:
        """Process navigation structure"""
        nav_items = []
        for nav in self.raw_data.get('navigation', []):
            for link in nav.get('children', []):
                if link.get('tag') == 'a':
                    nav_items.append({
                        "text": link.get('text', ''),
                        "href": link.get('href', ''),
                    })
        return nav_items
    
    def _extract_key_features(self) -> List[str]:
        """Extract key features or services"""
        features = []
        for section in self.raw_data.get('mainContent', []):
            if 'feature' in section.get('classes', []) or 'service' in section.get('classes', []):
                features.append(section.get('text', ''))
        return features
    
    def _extract_contact_info(self) -> Dict:
        """Extract contact information"""
        contact_info = {
            "email": self._find_emails(),
            "phone": self._find_phones(),
            "address": self._find_address()
        }
        return contact_info
    
    def _find_section_title(self, content: Dict) -> str:
        """Find title for a content section"""
        headers = ['h1', 'h2', 'h3', 'h4']
        for child in content.get('children', []):
            if child.get('tag', '') in headers:
                return child.get('text', '')
        return ''
    
    def _find_emails(self) -> List[str]:
        """Extract email addresses from content"""
        emails = []
        for link in self.raw_data.get('links', []):
            if link.get('href', '').startswith('mailto:'):
                emails.append(link.get('href').replace('mailto:', ''))
        return emails
    
    def _find_phones(self) -> List[str]:
        """Extract phone numbers from content"""
        phones = []
        for link in self.raw_data.get('links', []):
            if link.get('href', '').startswith('tel:'):
                phones.append(link.get('href').replace('tel:', ''))
        return phones
    
    def _find_address(self) -> str:
        """Extract physical address from content"""
        footer = self.raw_data.get('footer', [{}])[0]
        address = ''
        for child in footer.get('children', []):
            if 'address' in child.get('classes', []):
                address = child.get('text', '')
                break
        return address

    def _extract_all_links(self) -> List[Dict[str, str]]:
        """Extract all href links and their associated text from the content"""
        links = []
        for link in self.raw_data.get('links', []):
            href = link.get('href', '')
            text = link.get('text', '').strip()
            if href and text:
                links.append({
                    "text": text,
                    "href": href,
                    "location": link.get('location', 'unknown')
                })
        return links

    def save_processed_data(self, processed_data: Dict[str, Any], filepath: Path):
        """Save the processed data to a JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2)