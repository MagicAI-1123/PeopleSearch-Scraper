import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from app.components.info_phone import run_scraper as run_scraper_info
from app.components.truth_phone import run_scraper as run_scraper_truth

def run_async_scraper(scraper_func, phone):
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(scraper_func(phone))
        return result
    finally:
        loop.close()

async def run_scraper(phone):
    # Create a thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both scrapers to run in separate threads
        future_info = executor.submit(run_async_scraper, run_scraper_info, phone)
        future_truth = executor.submit(run_async_scraper, run_scraper_truth, phone)
        
        # Handle results and exceptions
        scrapers = [('Info Scraper', future_info), ('Truth Scraper', future_truth)]
        results = []
        for name, future in scrapers:
            try:
                result = future.result()
                results.append(result)
                print(f"{name} completed successfully")
            except Exception as e:
                print(f"{name} failed with error: {e}")
        
        print(results)

        return results

# Example usage
# if __name__ == "__main__":
#     phone = "9177839188"
#     results = run_scraper(phone)