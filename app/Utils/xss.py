import asyncio
# from seleniumwire import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv
import json
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
        profile_path = "C:/Xss1_SeleniumChromeProfile"

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
        # seleniumwire_options = {
        #     "proxy": {
        #         "http": f"https://{proxy_user}:{proxy_pass}@{proxy}",
        #         "https": f"https://{proxy_user}:{proxy_pass}@{proxy}",
        #     }
        # }
        

        webdriver_service = Service(ChromeDriverManager().install())

        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(
            service=webdriver_service,
            options=chrome_options,
            # seleniumwire_options=seleniumwire_options,
        )
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_page(self, url, keyword):
        try:
            # Navigate to the page
            self.driver.get(url)
            
            # Set cookies as before
            cookies = {
                'xf_user': '276225,AYhs1H46Ar7kilSe6eMEjtEjy1EW2plfRB63pdwx',
                'xf_csrf': 'L-CsFIuSPuYMe55W',
                'xf_session': 'w7AIx8OF80itLMR-C0n0Cnds_ko5saNB'
            }
            
            for name, value in cookies.items():
                self.driver.add_cookie({
                    'name': name,
                    'value': value,
                    'domain': 'xss.is'
                })
            
            # Refresh page to apply cookies
            self.driver.refresh()
            time.sleep(2)

            # First get the valid token from the page
            token = self.driver.execute_script("""
                return document.querySelector('input[name="_xfToken"]').value;
            """)
            
            print("Using token:", token)  # Debug print

            # Execute the search with the valid token
            result = self.driver.execute_script("""
                return new Promise((resolve, reject) => {
                    const formdata = new FormData();
                    formdata.append("_xfToken", arguments[1]);  // Use the token we got from the page
                    formdata.append("keywords", arguments[0]);
                    formdata.append("c[users]", "");
                    formdata.append("c[newer_than]", "");
                    formdata.append("c[older_than]", "");
                    formdata.append("order", "date");
                    formdata.append("search_type", "");
                    formdata.append("_xfRequestUri", "/search/");
                    formdata.append("_xfWithData", "1");
                    formdata.append("_xfResponseType", "json");

                    fetch("https://xss.is/search/search", {
                        method: "POST",
                        headers: {
                            "Accept": "application/json, text/javascript, */*; q=0.01",
                            "Accept-Language": "en-US,en;q=0.9",
                            "X-Requested-With": "XMLHttpRequest",
                            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": '"Windows"'
                        },
                        credentials: 'include',
                        body: formdata
                    })
                    .then(response => response.text())
                    .then(result => resolve(result))
                    .catch(error => reject(error));
                });
            """, keyword, token)  # Pass both keyword and token
            
            print("result: ", result)

            # Parse the redirect URL from the first response
            first_response = json.loads(result)
            redirect_url = first_response.get('redirect')
            
            if not redirect_url:
                print("No redirect URL found in response")
                return None

            # Execute the second request to get search results
            search_results = self.driver.execute_script("""
                return new Promise((resolve, reject) => {
                    fetch(arguments[0], {
                        method: "GET",
                        headers: {
                            "Referer": "https://xss.is/search/",
                            "Upgrade-Insecure-Requests": "1",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": '"Windows"'
                        },
                        credentials: 'include'
                    })
                    .then(response => response.text())
                    .then(result => resolve(result))
                    .catch(error => reject(error));
                });
            """, redirect_url)
            
            # print("search_results: ", search_results)
            
            # Save the search results as HTML file
            with open('search_results.html', 'w', encoding='utf-8') as f:
                f.write(search_results)
            
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(search_results, 'html.parser')
            
            result = []
            # Find all block-row elements that contain posts
            posts = soup.find_all('li', class_='block-row')
            print("Number of posts found:", len(posts))
            
            for post in posts:
                post_item = {}
                try:
                    # Get title - it's in an h3 with class contentRow-title > a
                    title_elem = post.find('h3', class_='contentRow-title')
                    if title_elem and title_elem.find('a'):
                        post_item["title"] = title_elem.find('a').get_text(strip=True)
                        post_item["url"] = title_elem.find('a')['href']
                    
                    # Get content - it's in div with class contentRow-snippet
                    content_elem = post.find('div', class_='contentRow-snippet')
                    if content_elem:
                        post_item["content"] = content_elem.get_text(strip=True)
                    
                    # Get minor info - includes author, post number, date, and forum
                    minor_elem = post.find('div', class_='contentRow-minor')
                    if minor_elem:
                        # Extract individual pieces of information
                        username = minor_elem.find('a', class_='username')
                        post_item["author"] = username.get_text(strip=True) if username else None
                        
                        # Get all list items
                        info_items = minor_elem.find_all('li')
                        for item in info_items:
                            if 'Post #' in item.get_text():
                                post_item["post_number"] = item.get_text(strip=True)
                            elif 'Forum:' in item.get_text():
                                post_item["forum"] = item.find('a').get_text(strip=True)
                            elif item.find('time'):
                                post_item["date"] = item.find('time')['datetime']
                    
                    result.append(post_item)
                except Exception as e:
                    print(f"Error parsing post: {e}")
            
            return {
                # 'initial_response': first_response,
                # 'search_results': search_results,
                'parsed_results': result
            }

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
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

# print(asyncio.run(run_scraper("AI Master")))