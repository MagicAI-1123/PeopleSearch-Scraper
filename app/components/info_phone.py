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

target_url = os.getenv("TARGET_URL")

input_type = "Phone"
phone = ""

class WebScraper:
    def __init__(self):  
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 20)  # Reduced from 20 to 10 seconds
        self.result = "\n****************Info Tracer****************\n"
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def initialize_driver(self):  
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')  
        chrome_options.add_argument("--user-data-dir=C:/Info_SeleniumChromeProfile")
        
        # chrome_options.add_argument("--headless=new")  # Modern headless mode
        
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
    
    async def scrape_website(self): 
        try:
            self.driver.get(target_url)
            await self.goto_search_tab(input_type)
            await self.input_phone()

            await self.scrape_profile_links()
            
            with open('infotracer_output_by_phone.txt', 'w') as file:
                file.write(self.result)
            print("Results have been written to infotracer_output_by_phone.txt")
            
            return self.result
        except Exception as e:
            print(e)

    async def goto_search_tab(self, input_type):
        global input_tab_position
        search_tabs = self.driver.execute_script("""return document.getElementsByClassName('search stabs')[0].getElementsByClassName('snav2')[0].getElementsByTagName('li')""")
        count = 0
        for search_tab in search_tabs:
            print("search_tab", search_tab)
            if search_tab.text.strip() == input_type:
                print("search_tab", search_tab.text)
                search_tab.click()
                break
            count += 1
        input_tab_position = count

    async def input_phone(self):
        phone_input = self.wait.until(EC.presence_of_element_located((By.ID, "phone")))
        phone_input.clear()
        phone_input.send_keys(phone)

        try:
            self.driver.execute_script(f"""document.querySelectorAll('[type="submit"]')[{input_tab_position}].click()""")
        except Exception as e:
            print("no submit button found:", str(e))
            pass

    async def get_person_link_list(self):
        person_list_table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        person_list_items = person_list_table.find_elements(By.TAG_NAME, "a")
        person_link_list = []
        for person_list_item in person_list_items:
            person_detail_url = person_list_item.get_attribute("href")
            person_link_list.append(person_detail_url)

        return person_link_list
        
    async def scrape_person_detail(self, person_link):
        try:
            self.driver.get(person_link)
        
        except Exception as e:
            print(e)
        
        # Use a list to collect data instead of immediate string concatenation
        result_parts = []
        result_parts.append("-----------------Person Details-----------------")
        
        try:
            person_detail_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r2-person")))
            
            try:
                name = person_detail_element.find_element(By.CLASS_NAME, "title").text
                result_parts.append(f"name: {name}")
                print(name)
            except Exception as e:
                print(f"Error getting name: {str(e)}")
                name = "N/A"
        except Exception as e:
            print(f"Error getting person details: {str(e)}")

        try:
            rows = person_detail_element.find_elements(By.CLASS_NAME, "row")
            for row in rows:
                try:
                    print(row.text)
                    result_parts.append(f"{row.text}")
                except Exception as e:
                    print(f"Error printing row text: {str(e)}")
        except Exception as e:
            print(f"Error getting rows: {str(e)}")
        
        result_parts.append("-----------------Address-----------------")
        
        try:
            address_rows = self.driver.find_elements(By.CLASS_NAME, "r2-address")
            for address_row in address_rows:
                address = "N/A"
                date = "N/A"
                try:
                    address = address_row.find_elements(By.CLASS_NAME, "r2-ai-li")[0].text
                except Exception as e:
                    print(f"Error getting address: {str(e)}")
                
                try:
                    date = address_row.find_elements(By.CLASS_NAME, "r2-ai-li")[1].text
                except Exception as e:
                    print(f"Error getting date: {str(e)}")
                
                print("address, date", address, date)
                result_parts.append(f"address: {address}, date: {date}")
        except Exception as e:
            print(f"Error processing address rows: {str(e)}")
        
        result_parts.append("-----------------Phone-----------------")

        try:
            phone_table = self.driver.find_element(By.ID, "phone_numbers")
            phone_rows = phone_table.find_elements(By.TAG_NAME, "tr")
            for phone_row in phone_rows:
                phone_number = "N/A"
                line_type = "N/A"
                date_reported = "N/A"
                try:
                    phone_number = phone_row.find_elements(By.TAG_NAME, "td")[1].text
                except Exception as e:
                    print(f"Error getting phone number: {str(e)}")
                try:
                    line_type = phone_row.find_elements(By.TAG_NAME, "td")[2].text
                except Exception as e:
                    print(f"Error getting line type: {str(e)}")
                try:
                    date_reported = phone_row.find_elements(By.TAG_NAME, "td")[3].text
                except Exception as e:
                    print(f"Error getting date reported: {str(e)}")
                print("phone_number, line_type, date_reported", phone_number, line_type, date_reported)
                result_parts.append(f"phone_number: {phone_number}, line_type: {line_type}, date_reported: {date_reported}")
        except Exception as e:
            print(f"Error processing phone table: {str(e)}")

        result_parts.append("-----------------Email-----------------")

        try:
            email_table = self.driver.find_element(By.ID, "email_addresses")
            email_rows = email_table.find_elements(By.TAG_NAME, "tr")
            for email_row in email_rows:
                name = "N/A"
                address = "N/A"
                ip_address = "N/A"
                email_address = "N/A"
                date_reported = "N/A"
                try:
                    name = email_row.find_elements(By.TAG_NAME, "td")[1].text
                except Exception as e:
                    print(f"Error getting email name: {str(e)}")
                try:
                    address = email_row.find_elements(By.TAG_NAME, "td")[2].text
                except Exception as e:
                    print(f"Error getting email address: {str(e)}")
                try:
                    ip_address = email_row.find_elements(By.TAG_NAME, "td")[3].text
                except Exception as e:
                    print(f"Error getting IP address: {str(e)}")
                try:
                    email_address = email_row.find_elements(By.TAG_NAME, "td")[4].text
                except Exception as e:
                    print(f"Error getting email address: {str(e)}")
                try:
                    date_reported = email_row.find_elements(By.TAG_NAME, "td")[5].text
                except Exception as e:
                    print(f"Error getting email date reported: {str(e)}")
                print("name, address, ip_address, email_address, date_reported", name, address, ip_address, email_address, date_reported)
                result_parts.append(f"name: {name}, address: {address}, ip_address: {ip_address}, email_address: {email_address}, date_reported: {date_reported}")
        except Exception as e:
            print(f"Error processing email table: {str(e)}")

        result_parts.append("-----------------Marriage-----------------")

        try:
            marriage_tables = self.driver.find_element(By.ID, "section-vital_marriage").find_elements(By.CLASS_NAME, "r2-data")
            # self.take_screenshot("marriage_section")
            for marriage_table in marriage_tables:
                try:
                    title = marriage_table.find_element(By.TAG_NAME, "h3").text
                    result_parts.append(f"title: {title}")
                    print("title", title)
                except Exception as e:
                    print(f"Error getting marriage title: {str(e)}")
                    title = "N/A"
                try:
                    marriage_rows = marriage_table.find_elements(By.TAG_NAME, "tr")
                    for marriage_row in marriage_rows:
                        key = "N/A"
                        value = "N/A"
                        try:
                            key = marriage_row.find_elements(By.TAG_NAME, "td")[0].text
                        except Exception as e:
                            print(f"Error getting marriage key: {str(e)}")
                        try:
                            value = marriage_row.find_elements(By.TAG_NAME, "td")[1].text
                        except Exception as e:
                            print(f"Error getting marriage value: {str(e)}")
                        print("key, value", key, value)
                        result_parts.append(f"key: {key}, value: {value}")
                except Exception as e:
                    print(f"Error processing marriage rows: {str(e)}")
        except Exception as e:
            print(f"Error processing marriage section: {str(e)}")

        result_parts.append("-----------------Licenses-----------------")

        try:
            license_tables = self.driver.execute_script("""return document.getElementById("section-professional_licenses").getElementsByClassName('accordion2 m-tb-m')""")
            # self.take_screenshot("licenses_section")
            for license_table in license_tables:
                print("here")
                try:
                    title_element = license_table.find_element(By.CLASS_NAME, "accordion2-header")
                    title = title_element.text
                    print("title", title)
                    result_parts.append(f"title: {title}")
                    # Use JavaScript to click the element, bypassing potential overlays
                    self.driver.execute_script("arguments[0].click();", title_element)
                    # Wait for any animations or overlays to disappear
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "accordion2-header"))
                    )
                    time.sleep(1)
                except Exception as e:
                    print(f"Error getting license title: {str(e)}")
                    title = "N/A"
                try:
                    license_rows = license_table.find_elements(By.TAG_NAME, "tr")
                    for license_row in license_rows:
                        key = "N/A"
                        value = "N/A"
                        try:
                            key = license_row.find_elements(By.TAG_NAME, "td")[0].text
                        except Exception as e:
                            print(f"Error getting license key: {str(e)}")
                        try:
                            value = license_row.find_elements(By.TAG_NAME, "td")[1].text
                        except Exception as e:
                            print(f"Error getting license value: {str(e)}")
                        print("key, value", key, value)
                        result_parts.append(f"key: {key}, value: {value}")
                except Exception as e:
                    print(f"Error processing license rows: {str(e)}")
        except Exception as e:
            print(f"Error processing license section: {str(e)}")

        result_parts.append("-----------------Court Records-----------------")

        result_parts.append('***** Criminal *****')
        try:
            court_records = self.driver.find_element(By.ID, "section-court_criminal")
            h3_elements = court_records.find_elements(By.TAG_NAME, "h3")
            table_elements = court_records.find_elements(By.CLASS_NAME, "r2-data")
            length = len(h3_elements)
            for i in range(length):
                try:
                    print("title", h3_elements[i].text)
                    result_parts.append(h3_elements[i].text)
                    rows = table_elements[i].find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            result_parts.append(f"{cells[0].text}: {cells[1].text}")
                        except Exception as e:
                            print(f"Error processing cell:  {str(e)}")
                    result_parts.append('\n')
                except Exception as e:
                    print(f"Error processing table: {str(e)}")
        except Exception as e:
            print(f"Error processing criminal records: {str(e)}")

        result_parts.append('***** Bankruptcies *****')

        try:
            court_records = self.driver.find_element(By.ID, "section-court_blj")
            h3_elements = court_records.find_elements(By.TAG_NAME, "h3")
            table_elements = court_records.find_elements(By.CLASS_NAME, "r2-data")
            length = len(h3_elements)
            for i in range(length):
                print("title", h3_elements[i].text)
                result_parts.append(h3_elements[i].text)
                rows = table_elements[i].find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    result_parts.append(f"{cells[0].text}: {cells[1].text}")
                result_parts.append('\n')
        except Exception as e:
            print(f"Error processing Bankruptcies records: {str(e)}")

        result_parts.append("-----------------Assets-----------------")
        try:
            assets_table = self.driver.find_element(By.CLASS_NAME, "table-automobiles")
            rows = assets_table.find_elements(By.TAG_NAME, "tr")
            length = len(rows)
            headers = rows[0].find_elements(By.TAG_NAME, "th")
            for i in range(1, length):
                cells = rows[i].find_elements(By.TAG_NAME, "td")
                for j in range(len(headers)):
                    result_parts.append(f"{headers[j].text}: {cells[j].text}")
                result_parts.append('\n')
        except Exception as e:
            print(f"Error processing assets: {str(e)}")
        
        self.result = '\n'.join(result_parts)
        

    async def scrape_profile_links(self):
        try:
            # Wait for the presence of at least one element with the class name
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-section")))
            
            # Find all elements with the class name
            profiles_sections = self.driver.find_elements(By.CLASS_NAME, "content-section")
            
            length = len(profiles_sections)
            for i in range(1, min(4, length)):
                title = profiles_sections[i].find_element(By.CLASS_NAME, "content-header").text
                self.result += f"{title}\n"
                
                body = profiles_sections[i].find_element(By.CLASS_NAME, "content-block")
                
                rows = body.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    self.result += f"{cells[0].text}: {cells[1].text}\n"
                self.result += '\n'
            
        except Exception as e:
            print(f"Error in scrape_profile_links: {str(e)}")
            return []
   
    def close_driver(self):  
        try:
            self.driver.quit()
        except Exception as e:
            print(e)


async def run_scraper(phone_input):
    global phone
    
    phone = phone_input
    
    scraper = WebScraper()
    
    return await scraper.scrape_website()