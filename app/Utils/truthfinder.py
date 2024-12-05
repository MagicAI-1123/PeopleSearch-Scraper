import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
import re
import json
from bs4 import BeautifulSoup  
from selenium.webdriver.support.ui import Select
import asyncio
from selenium.common.exceptions import NoSuchElementException

input_type = "Name"
first_name = ""
second_name = ""
middle_name = ""
city = ""
state = ""
age = 0
phone = ""
email = ""
street_address = ""
zip_code = ""

def extract_length(content: str):
    # Regular expression to find numbers
    numbers = re.findall(r'\d+', content)

    # Assuming there is at least one number, get the first one
    number = numbers[0] if numbers else 0
    return number

class WebScraper:
    # Create a WebScraper instance
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 15)  # Added explicit wait
        self.reports = []
        self.result = "-------------------------- Truthfinder -----------------------------\n\n"

    # Init the WebScraper instance
    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=C:/SeleniumChromeProfile")
        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.maximize_window()
        return driver
    
    
    async def scrape_website(self, url):
        try:
            self.driver.get(url)
            # time 
            if input_type == "Name":
                await self.input_full_name()
            elif input_type == "Phone":
                await self.input_phone()
            elif input_type == "Email":
                await self.input_email()
            elif input_type == "Address":
                await self.input_address()
            
            people_list = []
            
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results")))
                person_search_results = self.driver.find_elements(By.CLASS_NAME, "search-results")
                
                for person in person_search_results:
                    try:
                        time.sleep(2)
                        link = person.find_element(By.CLASS_NAME, 'button-link')
                        href = link.get_attribute('href')
                        people_list.append(href)
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        pass
            except NoSuchElementException:
                pass
            except Exception as e:
                pass
            
            if input_type == "Phone":
                tmp_people_list = people_list
                people_list = []
                
                for link in tmp_people_list:
                    self.driver.get(link)
                    print("phone link: ", link)

                    try:
                        owner_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "owner-history-subsection-item")))
                        first_person = owner_element.find_element(By.TAG_NAME, "a")
                        link = first_person.get_attribute('href')
                        people_list.append(link)
                        break
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        pass
            
            if input_type == "Address":
                tmp_people_list = people_list
                people_list = []
                
                for link in tmp_people_list:
                    self.driver.get(link)
                    try:
                        residents_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "record-subsection.residents-subsection")))
                        first_person = residents_element.find_element(By.TAG_NAME, "a")
                        link = first_person.get_attribute('href')
                        people_list.append(link)
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        pass
            
            for link in people_list:
                try:
                    await self.scrape_each_person(link)
                    break
                except Exception as e:
                    pass
        except Exception as e:
            import traceback
            pass

    async def input_full_name(self):
        if first_name:
            firstName_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'firstName')))
            firstName_element.clear()
            firstName_element.send_keys(first_name)
        
        if second_name:
            lastName_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'lastName')))
            lastName_element.clear()
            lastName_element.send_keys(second_name)
        
        if middle_name:  # Only handle middle name if it's not empty
            middleName_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'middleInitial')))
            middleName_element.clear()
            middleName_element.send_keys(middle_name)
        
        if city:
            city_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'city')))
            city_element.clear()
            city_element.send_keys(city)

        if state:
            state_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.NAME, "state"))))
            state_dropdown.select_by_visible_text(state)
            
        if age:
            age_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'age')))
            age_element.clear()
            age_element.send_keys(age)

        submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()

    async def input_phone(self):
        phone_tab = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "icon.tab-icon.phone")))
        phone_tab.click()
        
        phone_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'phone')))
        phone_element.clear()
        phone_element.send_keys(phone)
        
        submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()
        
    async def input_email(self):
        email_tab = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "icon.tab-icon.email")))
        email_tab.click()
        
        email_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_element.clear()
        email_element.send_keys(email)
        
        submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()
        
    async def input_address(self):
        address_tab = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "icon.tab-icon.pindrop")))
        address_tab.click()
        
        if street_address:
            address_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'street')))
            address_element.clear()
            address_element.send_keys(street_address)
            
        if city:
            city_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'city')))
            city_element.clear()
            city_element.send_keys(city)
            
        if state:
            state_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.NAME, "state"))))
            state_dropdown.select_by_visible_text(state)
            
        if zip_code:
            zip_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'zip')))
            zip_element.clear()
            zip_element.send_keys(zip_code)
        
        submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()

    async def scrape_each_person(self, link):
        try:
            self.driver.get(link)
            time.sleep(5)
            
            self.result += f"-------------------Personal Information-------------------\n"
            await self.get_personal_information()
            self.result += f"-------------------Contact Information-------------------\n"
            await self.get_contact_information()
            self.result += f"-------------------Location Information-------------------\n"
            await self.get_location_information()
            self.result += f"-------------------Business Information-------------------\n"
            await self.get_business_information()
            self.result += f"-------------------License Information-------------------\n"
            await self.get_license_information()
            self.result += f"-------------------Assets Information-------------------\n"
            await self.get_assets_information()
            
            time.sleep(1)
        except Exception as e:
            pass

    async def get_personal_information(self):
        try:
            personal_section = self.driver.find_element(By.CLASS_NAME, 'personal-section')
            try:
                name_element = personal_section.find_element(By.CLASS_NAME, 'names-subsection')
                name_items = name_element.find_elements(By.CLASS_NAME, 'ui-flex-item')
                for name_item in name_items:
                    try:
                        key = name_item.find_element(By.TAG_NAME, 'h6').text
                        value = name_item.find_element(By.TAG_NAME, 'h3').text
                        self.result += f"{key}: {value}\n"
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        pass
            except NoSuchElementException:
                pass
            except Exception as e:
                pass
        
            try:
                relatives_element = personal_section.find_element(By.CLASS_NAME, 'related-persons-subsection')
                relatives_items = relatives_element.find_elements(By.CLASS_NAME, 'relative-card')
                for relative in relatives_items:
                    try:
                        details = relative.find_element(By.CLASS_NAME, 'relative-details')
                        name = details.find_element(By.TAG_NAME, 'h3').text
                        self.result += f"Related Person: {name}\n"
                        items = details.find_elements(By.TAG_NAME, 'p')
                        for item in items:
                            self.result += f"{item.text}\n"
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        pass
            except NoSuchElementException:
                pass
            except Exception as e:
                pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
            
    async def get_contact_information(self):
        try:
            phone_section = self.driver.find_element(By.CLASS_NAME, 'phones-subsection')  
            phone_items = phone_section.find_elements(By.CLASS_NAME, 'phone-subsection-item')  

            for item in phone_items:  
                try:
                    phone_number = item.find_element(By.CLASS_NAME, 'phone-number').text  
                    line_type = item.find_element(By.XPATH, ".//p[contains(text(), 'Line Type')]/following-sibling::p/span").text  
                    carrier_location = item.find_element(By.XPATH, ".//p[contains(text(), 'Carrier Location')]/following-sibling::p/span").text  
                    
                    self.result += f'Phone Number: {phone_number}, Line Type: {line_type}, Carrier Location: {carrier_location}\n'
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
            
        try:
            email_section = self.driver.find_element(By.CLASS_NAME, 'emails-subsection')  
            email_items = email_section.find_elements(By.CLASS_NAME, 'section-table-header')  

            for email_item in email_items:  
                try:
                    email_address = email_item.find_element(By.TAG_NAME, 'h5').text  
                    self.result += f'Email Address: {email_address}\n'
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass

    async def get_location_information(self):
        try:
            sub_locations = self.driver.find_elements(By.CLASS_NAME, 'location-subsection-item')
            for sub_location in sub_locations:
                try:
                    await self.scrape_sub_location(sub_location)
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
            

    async def scrape_sub_location(self, sub_location):
        try:
            address = sub_location.find_element(By.CLASS_NAME, 'address-container')
            try:
                address_period = address.find_element(By.TAG_NAME, 'h6').text
                self.result += f"{address_period}\n"
            except NoSuchElementException:
                pass
            except Exception as e:
                pass
            
            try:
                address_text = address.find_element(By.TAG_NAME, 'p').text
                self.result += f"{address_text}\n"
            except NoSuchElementException:
                pass
            except Exception as e:
                pass
            
            try:
                address_title = address.find_element(By.CLASS_NAME, 'ui-text.medium').text
                self.result += f"{address_title}\n"
            except NoSuchElementException:
                pass
            except Exception as e:
                pass

            div_elements = address.find_elements(By.TAG_NAME, 'div')
            for dev_element in div_elements:
                try:
                    header = dev_element.find_element(By.TAG_NAME, 'h6').text
                    self.result += f"{header}\n"
                    p_tags = dev_element.find_elements(By.TAG_NAME, 'p')
                    for p_tag in p_tags:
                        self.result += f"{p_tag.text}\n"
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass

        try:
            location_details = sub_location.find_element(By.CLASS_NAME, 'location-details').find_elements(By.TAG_NAME, 'div')
            for detail in location_details:
                try:
                    header = detail.find_element(By.TAG_NAME, 'h6').text
                    self.result += f"{header}\n"
                    p_tags = detail.find_elements(By.TAG_NAME, 'p')
                    for p_tag in p_tags:
                        self.result += f"{p_tag.text}\n"
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
        
    async def get_business_information(self):
        try:
            await self.scrape_sub_tables('businesses-truncate')
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
            
        try:
            await self.scrape_sub_tables('corporate-filings-subsection')
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
            
        try:
            await self.scrape_sub_tables('employers-subsection')
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
        
    async def scrape_sub_tables(self, class_name):
        try:
            tables = self.driver.find_elements(By.CLASS_NAME, class_name)
            for table in tables:
                try:
                    sections = table.find_elements(By.CLASS_NAME, 'section-table')
                    for section in sections:
                        try:
                            header = section.find_elements(By.CLASS_NAME, 'section-table-header')[0].text
                            rows = section.find_elements(By.CLASS_NAME, 'section-table-row')
                            self.result += f"header: {header}\n"
                            for row in rows:
                                try:
                                    cells = row.find_elements(By.CLASS_NAME, 'section-table-cell')
                                    self.result += f"{cells[0].text}: {cells[1].text}\n"
                                except NoSuchElementException:
                                    pass
                                except Exception as e:
                                    pass
                        except NoSuchElementException:
                            pass
                        except Exception as e:
                            pass
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
     
    async def get_license_information(self):
        try:
            await self.scrape_sub_tables('professional-licenses-subsection-item')
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
        
    async def get_assets_information(self):
        try:
            show_buttons = self.driver.find_elements(By.CLASS_NAME, 'ui-accordion-toggle')
            for button in show_buttons:
                item = button.find_element(By.TAG_NAME, "span")
                if item and item.text == "Show":
                    self.driver.execute_script("arguments[0].click()", item)
            await self.scrape_sub_assets('property-subsection-item')
        except NoSuchElementException:
            pass
        except Exception as e:
            pass
    
    async def scrape_sub_assets(self, class_name):
        try:
            assets_elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            for assets_element in assets_elements:
                try:
                    title = assets_element.find_element(By.TAG_NAME, 'h2').text
                    self.result += f"{title}\n"
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
                
                try:
                    location = assets_element.find_element(By.CLASS_NAME, 'property-main-details')
                    self.result += f"{location.find_elements(By.TAG_NAME, 'h6')[0].text}\n"
                    self.result += f"{location.find_element(By.TAG_NAME, 'h3').text}\n"
                    self.result += f"{location.find_elements(By.TAG_NAME, 'h6')[1].text}\n"
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass

                try:
                    owner = assets_element.find_element(By.CLASS_NAME, 'current-owner-details')
                    self.result += f"{owner.find_element(By.TAG_NAME, 'h6').text}\n"
                    self.result += f"{owner.find_elements(By.TAG_NAME, 'h3')[0].text}\n"
                    self.result += f"{owner.find_elements(By.TAG_NAME, 'h3')[1].text}\n"
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
                
                try:
                    property_values = assets_element.find_element(By.CLASS_NAME, 'property-value-details')
                    property_values_items = property_values.find_elements(By.CLASS_NAME, 'property-value-detail')
                    for item in property_values_items:
                        try:
                            self.result += f"{item.find_element(By.TAG_NAME, 'h6').text}\n"
                            self.result += f"{item.find_elements(By.TAG_NAME, 'p')[0].text}\n"
                            self.result += f"{item.find_elements(By.TAG_NAME, 'p')[1].text}\n"
                        except NoSuchElementException:
                            pass
                except NoSuchElementException:
                    pass
                except Exception as e:
                    pass
                
                try:
                    property_details = assets_element.find_element(By.CLASS_NAME, 'property-details')
                    property_details_items = property_details.find_elements(By.CLASS_NAME, 'ui-flex-item')
                    for item in property_details_items:
                        try:
                            divs = item.find_elements(By.TAG_NAME, 'div')
                            for div in divs:
                                self.result += f"{div.find_element(By.TAG_NAME, 'h6').text}\n"
                                self.result += f"{div.find_element(By.TAG_NAME, 'p').text}\n"
                                self.result += "\n"
                                print("+++++++++++++++++++++++++")
                        except NoSuchElementException:
                            print("Property detail item elements not found")
                except NoSuchElementException:
                    print("Property details not found")
                except Exception as e:
                    print(e)
                
        except NoSuchElementException:
            print(f"Assets element not found for {class_name}")
        except Exception as e:
            print(f"Failed to scrape sub-assets for {class_name}:", str(e))
    
    async def close_driver(self):
        try:
            self.driver.close()
        except Exception as e:
            print("closing driver:", e)

async def run_scraper(user_data):
    global input_type, first_name, second_name, middle_name, city, state, age, phone, email, street_address, zip_code
    print("user_data.input_type: ", user_data.input_type)
    input_type = user_data.input_type
    first_name = user_data.first_name
    second_name = user_data.second_name
    middle_name = user_data.middle_name
    city = user_data.city
    state = user_data.state
    age = user_data.age
    phone = user_data.phone
    email = user_data.email
    street_address = user_data.street_address
    zip_code = user_data.zip_code
    
    
    scraper = WebScraper("ronaldo9441@gmail.com", "112112112ffF=")
    await scraper.scrape_website("https://www.truthfinder.com/dashboard")
    with open('truthfinder_output.txt', 'w') as file:
        file.write(scraper.result)
    await scraper.close_driver()
    return scraper.result
