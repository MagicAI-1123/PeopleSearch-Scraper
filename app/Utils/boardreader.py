import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import asyncio
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  
from selenium.webdriver.common.keys import Keys  
from datetime import datetime
from selenium.common.exceptions import TimeoutException

import urllib.parse

import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

keyword = ""

BASE_URL = "https://boardreader.com/s/{}.html;page={}"
PAGES_TO_SCRAPE = [1, 2, 3, 4]  # The pages we want to scrape

def keywords_to_url(base_url, keywords):  
    # Encode the keywords  
    encoded_keywords = urllib.parse.quote(keywords)  
    
    # Construct the full URL  
    full_url = base_url + encoded_keywords + '.html'
    
    return full_url 

class WebScraper:
    def __init__(self, url, page_num):  
        self.driver = self.initialize_driver(page_num)
        self.wait = WebDriverWait(self.driver, 10)  # Reduced from 20 to 10 seconds
        self.base_url = url
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.results = []
        
    def initialize_driver(self, page_num):  
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')  
        chrome_options.add_argument(f"--user-data-dir=C:/SeleniumChromeProfile_{page_num}")
        
        # Add performance-focused options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-browser-side-navigation')
        
        # More aggressive content blocking
        chrome_prefs = {
            "profile.default_content_setting_values": {
                "images": 2,
                "media_stream": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "auto_select_certificate": 2,
                "fullscreen": 2,
                "mouselock": 2,
                "mixed_script": 2,
                "media_stream_mic": 2,
                "media_stream_camera": 2,
                "protocol_handlers": 2,
                "ppapi_broker": 2,
                "automatic_downloads": 2,
                "midi_sysex": 2,
                "push_messaging": 2,
                "ssl_cert_decisions": 2,
                "metro_switch_to_desktop": 2,
                "protected_media_identifier": 2,
                "app_banner": 2,
                "site_engagement": 2,
                "durable_storage": 2
            }
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        webdriver_service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.maximize_window()
        return driver
    
    # def take_screenshot(self, step_name):
    #     """Helper method to take and save screenshots"""
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = f"{self.screenshot_dir}/{step_name}_{timestamp}.png"
    #     try:
    #         self.driver.save_screenshot(filename)
    #         print(f"Screenshot saved: {filename}")
    #     except Exception as e:
    #         print(f"Failed to take screenshot: {str(e)}")

    def scrape_website(self):
        try:
            target_url = self.base_url
            self.driver.get(target_url)
            
            time.sleep(3)
            print("here")
            
            post_lists = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mdl-list")))
            print("post_lists: ", post_lists)
            
            post_list_items = post_lists.find_elements(By.CLASS_NAME, "mdl-list__item")
            print("post_list_items: ", post_list_items)
            
            for post_list_item in post_list_items:
                print("post_list_item: ", post_list_item)
                title_element = post_list_item.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, "a")
                title = title_element.text
                print("title: ", title)
                
                link = title_element.get_attribute("href")
                print("link: ", link)
                
                first_info = post_list_item.find_element(By.CLASS_NAME, "first-info").find_elements(By.TAG_NAME, "span")
                date_text = first_info[0].text
                print("date_text: ", date_text)
                
                user_name = first_info[1].text
                print("user_name: ", user_name)
                
                context = post_list_item.find_element(By.CLASS_NAME, "text").text
                print("context: ", context)
                
                self.results.append({
                    "title": title,
                    "link": link,
                    "date_text": date_text,
                    "user_name": user_name,
                    "context": context
                })
                
            return self.results

        except Exception as e:
            print(e)
        finally:
            # Ensure driver is closed
            self.close_driver()

    def close_driver(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(e)

def run_single_scraper(keyword: str, page_num: int):
    try:
        url = BASE_URL.format(keyword, page_num)
        scraper = WebScraper(url, page_num)
        result = scraper.scrape_website()
        print(f"Scraper for {keyword} page {page_num} completed successfully")
        return {f"page_{page_num}": result}
    except Exception as e:
        print(f"Scraper for {keyword} page {page_num} failed with error: {e}")
        return {f"page_{page_num}": []}
    
def run_parallel_scrapers(keyword: str) -> Dict[str, List]:
    # result = []
    # for i in range(1, 5):
    #     run_single_scraper(keyword, i)
    # Create a thread pool with 4 workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all scraping tasks
        future_to_page = {
            executor.submit(run_single_scraper, keyword, page): page 
            for page in PAGES_TO_SCRAPE
        }
        
        # Collect all results
        all_results = {}
        for future in future_to_page:
            try:
                result = future.result()
                all_results.update(result)
            except Exception as e:
                page = future_to_page[future]
                print(f"Scraper for page {page} failed with error: {e}")
                all_results[f"page_{page}"] = []
                
        return all_results

def run_scraper(_keyword):
    keyword = _keyword  # This can be passed as an argument or input
    
    results = run_parallel_scrapers(keyword)
    print("All results:", results)
    return results