from typing import Dict, List, Any
import json
from pathlib import Path
import groq
import os
from dotenv import load_dotenv
from collections import defaultdict
import re
from datetime import datetime
class ChatbotDatasetGenerator:
    def __init__(self, processed_data_path: Path):
        load_dotenv()
        self.groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.processed_data = self._load_data(processed_data_path)
    
    def _load_data(self, filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_context_blocks(self) -> List[Dict]:
        """Create context blocks from processed data"""
        blocks = []
        
        # Website overview block
        overview = self.processed_data.get('website_overview', {})
        blocks.append({
            "type": "overview",
            "content": f"Website: {overview.get('title')}. {overview.get('meta_description')}",
            "topics": overview.get('main_topics', [])
        })
        
        # Content sections block
        for section in self.processed_data.get('content_sections', []):
            if section.get('content'):
                blocks.append({
                    "type": "content",
                    "title": section.get('title', ''),
                    "content": section.get('content')
                })
        
        # Navigation and links block
        blocks.append({
            "type": "navigation",
            "links": self.processed_data.get('all_links', [])
        })
        
        return blocks
    
    def _categorize_qa_pairs(self, dataset: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize QA pairs into topic groups"""
        categories = {
            'general_info': r'(about|company|website|who|what is)',
            'services': r'(service|offer|provide|solution|development)',
            'contact': r'(contact|email|phone|reach|location)',
            'features': r'(feature|capability|can you|able to)',
            'technical': r'(technical|technology|platform|software|system)',
            'pricing': r'(price|cost|package|payment)',
            'process': r'(process|how|steps|workflow)',
            'support': r'(support|help|assist|guide)',
        }
        
        categorized_data = defaultdict(list)
        
        for qa_pair in dataset:
            question = qa_pair['question'].lower()
            categorized = False
            
            for category, pattern in categories.items():
                if re.search(pattern, question):
                    categorized_data[category].append(qa_pair)
                    categorized = True
                    break
            
            if not categorized:
                categorized_data['other'].append(qa_pair)
        
        return dict(categorized_data)
    
    def generate_dataset(self) -> List[Dict]:
        """Generate QA pairs from context blocks"""
        try:
            context_blocks = self._create_context_blocks()
            dataset = []
            print(f"Processing {len(context_blocks)} context blocks...")

            for i, block in enumerate(context_blocks, 1):
                try:
                    # Limit content size for API
                    content = str(block)[:4000]  # Prevent token limit issues
                    
                    response = self.groq_client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "Create natural Q&A pairs for a website chatbot. Format: [{\"question\": \"...\", \"answer\": \"...\"}]"
                            },
                            {
                                "role": "user",
                                "content": f"Generate 5 Q&A pairs for this content: {content}"
                            }
                        ],
                        model="mixtral-8x7b-32768",
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    qa_pairs = json.loads(response.choices[0].message.content)
                    dataset.extend(qa_pairs)
                    print(f"Processed block {i}/{len(context_blocks)}")
                    
                except Exception as e:
                    print(f"Error processing block {i}: {str(e)}")
                    continue

            return dataset
            
        except Exception as e:
            print(f"Error generating dataset: {str(e)}")
            return []
        
    def generate_categorized_dataset(self) -> Dict[str, Any]:
        """Generate and categorize dataset"""
        raw_dataset = self.generate_dataset()
        categorized_dataset = self._categorize_qa_pairs(raw_dataset)
        
        # Add metadata
        final_dataset = {
            'metadata': {
                'total_qa_pairs': len(raw_dataset),
                'categories': list(categorized_dataset.keys()),
                'generated_at': datetime.now().isoformat()
            },
            'categories': categorized_dataset
        }
        
        return final_dataset

    def save_categorized_dataset(self, dataset: Dict[str, Any], output_path: Path):
        """Save the categorized dataset"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        print(f"Categorized dataset saved to {output_path}")
