import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from app.components.info_email import run_scraper as run_scraper_info
from app.components.truth_email import run_scraper as run_scraper_truth

def run_async_scraper(scraper_func, email):
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(scraper_func(email))
        return result
    finally:
        loop.close()

async def run_scraper(email):
    # Create a thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both scrapers to run in separate threads
        future_info = executor.submit(run_async_scraper, run_scraper_info, email)
        future_truth = executor.submit(run_async_scraper, run_scraper_truth, email)
        
        # Handle results and exceptions
        # scrapers = [('Info Scraper', future_info), ('Truth Scraper', future_truth)]
        scrapers = [('Info Scraper', future_info)]
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

# # Example usage
# if __name__ == "__main__":
#     email = "rbearman@gmail.com"
#     results = run_scraper(email)