from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from Scraper import Scraper
# import json

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
email = "ztataz04@gmail.com"
password = "DR#(Li,g#2Q.F,Z"
linkedin_url = 'https://www.linkedin.com/in/denniskoutoudis/'

obj = Scraper(driver, email, password)
obj.scrape_profile(linkedin_url)
data = obj.get_data()

# [] = for i obj.scrape_profile([i]).data

# data_json = json.dumps(data)

driver.quit()

# print(data_json)

for key, value in data.items():
    print(key, ': ', value)
