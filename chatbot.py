from typing import Dict, List, Any
import json
from pathlib import Path
from groq import Groq
import os
import random
from dotenv import load_dotenv

class WebsiteChatbot:
    def __init__(self, dataset_path: Path):
        load_dotenv()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.dataset = self._load_dataset(dataset_path)
        self.categories = self.dataset.get('metadata', {}).get('categories', [])
        self.qa_pairs = self.dataset.get('categories', {})
        self.common_greetings = {
            'hello': 'Hello! I can help you with the following categories:\n',
            'hi': 'Hi there! Here are the topics I can help you with:\n',
            'hey': 'Hey! These are the areas I can assist you with:\n',
            'good morning': 'Good morning! I can help you with these topics:\n',
            'good afternoon': 'Good afternoon! Here are the topics I know about:\n',
            'good evening': 'Good evening! I can assist you with the following:\n'
        }
        self.exit_phrases = {
            'bye': 'Goodbye! Have a great day!',
            'thank you': 'You\'re welcome! Goodbye!',
            'thanks': 'You\'re welcome! Have a great day!',
            'exit': 'Goodbye! Feel free to come back if you have more questions!',
            'quit': 'Goodbye! Hope I was helpful!'
        }

    def _load_dataset(self, filepath: Path) -> Dict[str, Any]:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _find_exact_match(self, user_input: str) -> Dict[str, str]:
        user_input_lower = user_input.lower().strip()
        for category, qa_list in self.qa_pairs.items():
            for qa in qa_list:
                if qa['question'].lower().strip() == user_input_lower:
                    return {'answer': qa['answer'], 'category': category}
        return None

    def _find_relevant_qa(self, user_input: str, max_pairs: int = 3) -> List[Dict]:
        relevant_pairs = []
        user_input_lower = user_input.lower()
        
        for category, qa_list in self.qa_pairs.items():
            for qa in qa_list:
                if any(word.lower() in qa['question'].lower() for word in user_input.split()):
                    qa['category'] = category
                    relevant_pairs.append(qa)
                    if len(relevant_pairs) >= max_pairs:
                        return relevant_pairs
        return relevant_pairs

    def _format_categories(self) -> str:
        return '\n'.join(f"- {category.replace('_', ' ').title()}" for category in self.categories)

    def _handle_greeting(self, user_input: str) -> str:
        user_input_lower = user_input.lower()
        for greeting, response in self.common_greetings.items():
            if user_input_lower.startswith(greeting):
                return response
        return None

    def _get_random_questions(self, category: str, num_questions: int = 5) -> List[str]:
        if category in self.qa_pairs:
            qa_list = self.qa_pairs[category]
            selected = random.sample(qa_list, min(num_questions, len(qa_list)))
            return [qa['question'] for qa in selected]
        return []

    def _is_category_selection(self, user_input: str) -> str:
        user_input_clean = user_input.lower().strip()
        for category in self.categories:
            if category.lower().replace('_', ' ') in user_input_clean:
                return category
        return None
    
    def _is_exact_category(self, user_input: str) -> str:
        """Check if input exactly matches a category name"""
        user_input_clean = user_input.lower().strip()
        for category in self.categories:
            if category.lower() == user_input_clean:
                return category
        return None

    def get_response(self, user_input: str) -> str:
        try:
            # Handle greetings
            greeting_response = self._handle_greeting(user_input)
            if greeting_response:
                return f"{greeting_response}{self._format_categories()}"

            # Check for category selection
            selected_category = self._is_category_selection(user_input)
            if selected_category:
                questions = self._get_random_questions(selected_category)
                if questions:
                    return f"Here are some questions about {selected_category.replace('_', ' ').title()}:\n" + \
                           '\n'.join(f"- {q}" for q in questions)

            # Look for exact match
            exact_match = self._find_exact_match(user_input)
            if exact_match:
                return exact_match['answer']

            # Find relevant QA pairs
            relevant_qa = self._find_relevant_qa(user_input)
            if relevant_qa:
                context = json.dumps(relevant_qa)
                response = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful chatbot. Answer based on the provided QA pairs."
                        },
                        {
                            "role": "user",
                            "content": f"Context: {context}\nQuestion: {user_input}"
                        }
                    ],
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
        
    def _is_exit_phrase(self, user_input: str) -> str:
        """Check if user wants to exit"""
        user_input_lower = user_input.lower().strip()
        for phrase in self.exit_phrases:
            if phrase in user_input_lower:
                return self.exit_phrases[phrase]
        return None

    def start_chat(self):
        print("Welcome to the Website Chatbot! Type 'quit' to exit.")
        print("\nAvailable categories:")
        print(self._format_categories())
        
        while True:
            user_input = input("\nYou: ")
            
            # Check for exit phrases
            exit_response = self._is_exit_phrase(user_input)
            if exit_response:
                print(f"\nBot: {exit_response}")
                break
            
            response = self.get_response(user_input)
            print(f"\nBot: {response}")

def main():
    try:
        dataset_path = Path("data/chatbot_dataset.json")
        chatbot = WebsiteChatbot(dataset_path)
        chatbot.start_chat()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()