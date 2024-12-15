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

target_url = os.getenv("TARGET_URL")
input_tab_position = 0

input_type = ""
first_name = ""
last_name = ""
city = ""
state_name = ""
phone = ""
email = ""
address = ""
license = ""

class WebScraper:
    def __init__(self):  
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 20)  # Reduced from 20 to 10 seconds
        self.result = "-------------------------- Infotracer -----------------------------\n\n"
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def initialize_driver(self):  
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')  
        chrome_options.add_argument("--user-data-dir=C:/Info_SeleniumChromeProfile")
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        
        # chrome_options.add_argument("--headless=new")  # Modern headless mode
        
        # Add performance-focused options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-browser-side-navigation')
        
        # More aggressive content blocking
        # chrome_prefs = {
        #     "profile.default_content_setting_values": {
        #         "images": 2,
        #         "media_stream": 2,
        #         "plugins": 2,
        #         "popups": 2,
        #         "geolocation": 2,
        #         "notifications": 2,
        #         "auto_select_certificate": 2,
        #         "fullscreen": 2,
        #         "mouselock": 2,
        #         "mixed_script": 2,
        #         "media_stream_mic": 2,
        #         "media_stream_camera": 2,
        #         "protocol_handlers": 2,
        #         "ppapi_broker": 2,
        #         "automatic_downloads": 2,
        #         "midi_sysex": 2,
        #         "push_messaging": 2,
        #         "ssl_cert_decisions": 2,
        #         "metro_switch_to_desktop": 2,
        #         "protected_media_identifier": 2,
        #         "app_banner": 2,
        #         "site_engagement": 2,
        #         "durable_storage": 2
        #     }
        # }
        # chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        webdriver_service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        # driver.maximize_window()
        return driver
    
    async def scrape_website(self):
        # time.sleep(2)
        try:
            print("here")
            self.driver.get(target_url)
            # sign in
            # await self.sign_in()
            # search
            await self.goto_search_tab(input_type)
            
            if input_type == "Name":
                await self.input_full_name()
                await self.click_confirm_button()

                person_link_list = await self.get_person_link_list()
                print("person_link_list: ", person_link_list)
                for person_link in person_link_list:
                    await self.scrape_person_detail(person_link)
                    break
            
            elif input_type == "Phone" or input_type == "Email":
                if input_type == "Phone":
                    await self.input_phone()
                elif input_type == "Email":
                    await self.input_email()
                
                profile_link_list = await self.scrape_profile_links()
                print("profile_link_list: ", profile_link_list)
                for profile_link in profile_link_list:
                    self.driver.get(profile_link)
                    
                    person_link_list = await self.get_person_link_list()
                    print("person_link_list: ", person_link_list)
                    for person_link in person_link_list:
                        await self.scrape_person_detail(person_link)
                        print("person_link: ", person_link)
                        break
                    break

            elif input_type == "Address":
                await self.input_address()
                await self.scrape_address_detail()

            elif input_type == "License":
                await self.input_license()
                await self.scrape_license_detail()
            
            with open('infotracer_output.txt', 'w') as file:
                file.write(self.result)
            print("Results have been written to infotracer_output.txt")
        
            return self.result
        except Exception as e:
            print(e)
            self.close_driver()

    async def sign_in(self):
        try:
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_input.clear()
            time.sleep(1)

            email_input.send_keys(os.getenv("EMAIL"))

            password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_input.clear()
            time.sleep(1)

            password_input.send_keys(os.getenv("PASSWORD"))

            sign_in_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            sign_in_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)

    async def goto_search_tab(self, input_type):
        if input_type == "Address" or input_type == "License":
            return
        # try:
        #     time.sleep(1)
        #     self.driver.execute_script("document.getElementById('fcra-agree').click()")
        #     time.sleep(1)
        # except Exception as e:
        #     print("no fcra-agree button found:", str(e))
        #     pass
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

    async def input_full_name(self):
        first_name_input = self.wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        first_name_input.clear()
        time.sleep(1)
        first_name_input.send_keys(first_name)

        last_name_input = self.wait.until(EC.presence_of_element_located((By.ID, "lastName")))
        last_name_input.clear()
        time.sleep(1)
        last_name_input.send_keys(last_name)        
        
        state_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "state"))))
        state_dropdown.select_by_visible_text(state_name)

        try:
            self.driver.execute_script(f"""document.querySelectorAll('[type="submit"]')[{input_tab_position}].click()""")
        except Exception as e:
            print("no submit button found:", str(e))
            pass

    async def input_phone(self):
        phone_input = self.wait.until(EC.presence_of_element_located((By.ID, "phone")))
        phone_input.clear()
        time.sleep(1)
        phone_input.send_keys(phone)
        
        try:
            self.driver.execute_script(f"""document.querySelectorAll('[type="submit"]')[{input_tab_position}].click()""")
        except Exception as e:
            print("no submit button found:", str(e))
            pass
    
    async def input_address(self):
        input_type_tab = self.wait.until(EC.presence_of_element_located((By.ID, "search")))
        self.driver.execute_script("arguments[0].getElementsByTagName('li')[4].getElementsByTagName('a')[1].click()", input_type_tab)
        time.sleep(2)
        address_input = self.driver.execute_script("""return document.querySelector('[name="address"]')""");
        address_input.clear()
        time.sleep(1)
        address_input.send_keys(address)
        
        try:
            self.driver.execute_script("""document.querySelectorAll('[type="submit"]')[0].click()""")
            print("here")
            time.sleep(10)
        except Exception as e:
            print("no submit button found:", str(e))
            pass
    
    async def input_license(self):
        input_type_tab = self.wait.until(EC.presence_of_element_located((By.ID, "search")))
        self.driver.execute_script("arguments[0].getElementsByTagName('li')[5].getElementsByTagName('a')[1].click()", input_type_tab)
        time.sleep(2)

        license_input = self.wait.until(EC.presence_of_element_located((By.ID, "plateInput")))
        license_input.clear()
        time.sleep(1)
        license_input.send_keys(license)
        
        state_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "plateState"))))
        state_dropdown.select_by_visible_text(state_name)
        
        try:
            self.driver.execute_script("""document.querySelectorAll('[type="submit"]')[0].click()""")
        except Exception as e:
            print("no submit button found:", str(e))
            pass
        
    async def input_email(self):
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.clear()
        time.sleep(1)
        email_input.send_keys(email)

        try:
            self.driver.execute_script(f"""document.querySelectorAll('[type="submit"]')[{input_tab_position}].click()""")
        except Exception as e:
            print("no submit button found:", str(e))
            pass

    async def click_confirm_button(self):
        try:
            time.sleep(1)
            self.driver.execute_script("document.getElementsByClassName('form-btn lbox-btn-agree fcra-agree')[1].click()")
            time.sleep(1)
        except Exception as e:
            print("no fcra-agree button found:", str(e))
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
            assets_table = driver.execute_script("return document.querySelector('.table-automobiles');")  
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
            profile_link_item = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fcralb-nametobgreport-link")))
            
            # Find all elements with the class name
            profile_links = self.driver.find_elements(By.CLASS_NAME, "fcralb-nametobgreport-link")
            
            profile_link_list = []
            for profile_link_item in profile_links:
                person_detail_url = profile_link_item.get_attribute("href")
                profile_link_list.append(person_detail_url)

            return profile_link_list
        except Exception as e:
            print(f"Error in scrape_profile_links: {str(e)}")
            return []
    
    async def scrape_address_detail(self):
        self.result += "-----------------Address Detail-----------------\n"
        owner_section = self.wait.until(EC.presence_of_element_located((By.ID, "section_owners")))
        first_section = owner_section.find_element(By.CLASS_NAME, 'bdy').find_element(By.CLASS_NAME, 'sec')
        owner_name = first_section.find_elements(By.CLASS_NAME, 'r-h3')[0].text
        print("owner_name", owner_name)
        self.result += f"owner_name: {owner_name}\n"
        mailing_address = first_section.find_elements(By.CLASS_NAME, 'r-h3')[1].text
        print("mailing_address", mailing_address)
        self.result += f"mailing_address: {mailing_address}\n"
        
        value_section = self.wait.until(EC.presence_of_element_located((By.ID, "section_values")))
        values = value_section.find_element(By.CLASS_NAME, "bdy").find_elements(By.CLASS_NAME, "col")
        for value in values:
            title = value.find_element(By.CLASS_NAME, "ttl").text
            value_text = value.find_element(By.CLASS_NAME, "val").text
            print("title, value_text", title, value_text)
            self.result += f"{title}: {value_text}\n"
    
    async def scrape_license_detail(self):
        self.result += "-----------------License Detail-----------------\n"
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-section")))
        content_sections = self.driver.find_elements(By.CLASS_NAME, "content-section")
        for content_section in content_sections:
            try:
                content_header = content_section.find_element(By.CLASS_NAME, "content-header")
                header_element = content_header.find_element(By.TAG_NAME, "h2")
                self.result += f"{header_element.text}\n"
            except Exception as e:
                continue
            try:
                try:
                    content_blocks = content_section.find_elements(By.CLASS_NAME, "content-block")
                    for content_block in content_blocks:
                        try:
                            tables = content_block.find_elements(By.TAG_NAME, "table")
                            for table in tables:
                                try:
                                    rows = table.find_elements(By.TAG_NAME, "tr")
                                    for row in rows:
                                        try:
                                            cells = row.find_elements(By.TAG_NAME, "td")
                                            self.result += f"{cells[0].text}: {cells[1].text}\n"
                                        except Exception as e:
                                            print(f"Error processing row: {str(e)}")
                                            continue
                                except Exception as e:
                                    print(f"Error processing table: {str(e)}")
                                    continue
                        except Exception as e:
                            print(f"Error processing content block: {str(e)}")
                            continue
                        self.result += '\n'
                except Exception as e:
                    print(f"Error getting content blocks: {str(e)}")
                    pass
            except Exception as e:
                continue
    
    def close_driver(self):  
        try:
            self.driver.quit()
        except Exception as e:
            print(e)


async def run_scraper(user_data):
    global first_name, last_name, state_name, phone, email, address, license, city, input_type
    
    input_type = user_data.input_type
    first_name = user_data.first_name
    last_name = user_data.second_name
    city = user_data.city
    state_name = user_data.state
    phone = user_data.phone
    email = user_data.email
    address = user_data.street_address
    license = user_data.license
    
    scraper = WebScraper()
    
    return await scraper.scrape_website()