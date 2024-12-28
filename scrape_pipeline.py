import asyncio
from pathlib import Path
import json
from scrapper import WebScraper
from preprocess import DataProcessor
from chatbot_data import ChatbotDatasetGenerator

class WebsiteChatbotPipeline:
    def __init__(self, url: str):
        self.url = url
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    async def run(self):
        try:
            # Step 1: Scrape website
            print(f"\n1. Scraping website: {self.url}")
            scraper = await WebScraper.create()
            scraped_data_path = await scraper.scrape_website(self.url)
            print(f"Scraping completed. Data saved to: {scraped_data_path}")
            
            # Step 2: Process data
            print("\n2. Processing scraped data...")
            processor = DataProcessor(scraped_data_path)
            structured_data = processor.process_for_chatgpt()
            processed_data_path = self.data_dir / "processed_data.json"
            processor.save_processed_data(structured_data, processed_data_path)
            print(f"Processing completed. Data saved to: {processed_data_path}")
            
            # Step 3: Generate chatbot dataset
            print("\n3. Generating chatbot dataset...")
            generator = ChatbotDatasetGenerator(processed_data_path)
            dataset = generator.generate_categorized_dataset()
            dataset_path = self.data_dir / "chatbot_dataset.json"
            generator.save_categorized_dataset(dataset, dataset_path)
            print(f"Dataset generation completed. Saved to: {dataset_path}")
            
            print("\nPipeline completed successfully!")
            return dataset_path
            
        except Exception as e:
            print(f"Pipeline error: {str(e)}")
            raise
        
        finally:
            if 'scraper' in locals():
                await scraper.close()

async def main():
    try:
        url = input("Enter the website URL to scrape: ")
        pipeline = WebsiteChatbotPipeline(url)
        await pipeline.run()
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())