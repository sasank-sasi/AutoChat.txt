import asyncio
from scrapper import WebScraper

async def main():
    try:
        # Initialize scraper using factory method
        scraper = await WebScraper.create()
        
        url = "https://relinns.com/"
        print(f"Starting to scrape: {url}")
        
        filepath = await scraper.scrape_website(url)
        print(f"Scraping completed. Data saved to: {filepath}")
        
        scraped_data = WebScraper.load_scraped_data(filepath)
        print("\nWebsite Information:")
        print(f"Title: {scraped_data['title']}")
        print(f"Number of links: {len(scraped_data['links'])}")
        print(f"Navigation items: {len(scraped_data['navigation'])}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    
    finally:
        if scraper:
            await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())