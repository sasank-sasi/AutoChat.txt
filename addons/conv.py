from pathlib import Path
from chatbot_data import ChatbotDatasetGenerator

def main():
    try:
        processed_data_path = Path("data/processed_data.json")
        generator = ChatbotDatasetGenerator(processed_data_path)
        
        print("Generating categorized dataset...")
        dataset = generator.generate_categorized_dataset()
        
        output_path = Path("data/chatbot_dataset.json")
        generator.save_categorized_dataset(dataset, output_path)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()