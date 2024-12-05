import asyncio
from seleniumwire import webdriver

# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

# from vivino_api import get_link


class WineDetailScraper:
    def __init__(self, proxy_user, proxy_pass):
        """Init the class

        Initialize the wine detail scraper with proxy settings for extracting comprehensive wine information

        Args:
            proxy_user (str): IPRoyal proxy username
            proxy_pass (str): IPRoyal proxy password
        """
        # Setting up Chrome options
        proxy = "geo.beyondproxy.io:5959"
        profile_path = "C:/Xss_SeleniumChromeProfile"

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument(
            "--blink-settings=imagesEnabled=false"
        )  # Disable images
        chrome_options.add_argument("--disable-css")  # Disable CSS
        # Performance optimization arguments
        chrome_options.add_argument(
            "--disable-gpu"
        )  # Disable GPU hardware acceleration
        chrome_options.add_argument(
            "--disable-dev-shm-usage"
        )  # Overcome limited resource problems
        chrome_options.add_argument("--disable-extensions")  # Disable extensions
        chrome_options.add_argument("--disable-notifications")  # Disable notifications
        chrome_options.add_argument("--disable-infobars")  # Disable infobars
        chrome_options.add_argument("--disable-javascript")  # Disable JavaScript
        chrome_options.add_argument(
            "--disable-popup-blocking"
        )  # Disable popup blocking
        chrome_options.add_argument("--disable-web-security")  # Disable web security
        chrome_options.add_argument("--dns-prefetch-disable")  # Disable DNS prefetching
        chrome_options.add_argument(
            "--disable-browser-side-navigation"
        )  # Disable browser side navigation
        # chrome_options.add_argument('--headless')# Run headless if you don't need a GUI
        chrome_options.add_argument(
            f"--user-data-dir={profile_path}"
        )  # Use the same path

        # Configure Selenium Wire to use IPRoyal proxy
        seleniumwire_options = {
            "proxy": {
                "http": f"https://{proxy_user}:{proxy_pass}@{proxy}",
                "https": f"https://{proxy_user}:{proxy_pass}@{proxy}",
            }
        }
        

        webdriver_service = Service(ChromeDriverManager().install())

        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(
            service=webdriver_service,
            options=chrome_options,
            seleniumwire_options=seleniumwire_options,
        )
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_page(self, url, keyword):
        try:

            # Navigate to the page
            self.driver.get(url)
            
            time.sleep(5000)
            
            # keywords_element = self.driver.find_element(By.NAME, "keywords")
            keywords_element = self.driver.execute_script("return document.getElementsByName('keywords')[1]")
            print('here')
            keywords_element.clear()
            keywords_element.send_keys(keyword)
            
            
            
            self.driver.execute_script("document.getElementsByClassName('formSubmitRow-controls')[0].getElementsByClassName('button--icon--search')[0].click()")
            # time.sleep(5)
            
            page_nav_element = self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, "pageNav-main"))
            page_elements = page_nav_element.find_elements(By.TAG_NAME, "a")
            number_of_pages = int(page_elements[-1].text)
            print("number_of_pages: ", number_of_pages)
            current_url = self.driver.current_url
            result = []
            for i in range(1, number_of_pages + 1):
                tmp_link = current_url + f"&page={i}"
                print("tmp_link: ", tmp_link)
                self.driver.get(tmp_link)
                p_body_element = self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, "p-body-content"))
                
                p_body_element = self.driver.execute_script("return document.getElementsByClassName('p-body-content')[0]")
                
                posts = p_body_element.find_elements(By.CLASS_NAME, "block-row")
                print("posts: ", posts)
                print('len: ', len(posts))
                for post in posts:
                    post_item = {}
                    try:
                        title = post.find_element(By.CLASS_NAME, "contentRow-title").text
                        post_item["title"] = title
                        
                        body = post.find_element(By.CLASS_NAME, "contentRow-snippet").text
                        post_item["content"] = body
                        
                        minor = post.find_element(By.CLASS_NAME, "contentRow-minor").text
                        post_item["minor"] = minor
                        result.append(post_item)
                        
                        print(post_item)
                    except Exception as e:
                        print(f"An error occurred: {e}")
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Clean up and close the browser instance
            self.driver.close()


async def run_scraper(keyword):
    # Usage
    proxy_name = os.getenv("PROXY_USERNAME")
    proxy_pass = os.getenv("PROXY_PASSWORD")
    print(proxy_name)
    print(proxy_pass)
    link = "https://xss.is/search/"
    scraper = WineDetailScraper(proxy_name, proxy_pass)
    
    return scraper.scrape_page(link, keyword)
    # print(text_data)
