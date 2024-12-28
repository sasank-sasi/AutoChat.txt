from pathlib import Path
import json
from preprocess import DataProcessor

# Initialize processor with scraped data
scraped_data_path = Path("data/scraped_data.json")
processor = DataProcessor(scraped_data_path)

# Get structured data for ChatGPT
structured_data = processor.process_for_chatgpt()

# Save the structured data to a file
output_path = Path("data/processed_data.json")
processor.save_processed_data(structured_data, output_path)

# Print the structured data
print(json.dumps(structured_data, indent=2))