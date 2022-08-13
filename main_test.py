from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from Scraper import Scraper
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# driver = webdriver.Chrome()
email = "ztataz04@gmail.com"
password = "DR#(Li,g#2Q.F,Z"
linkedin_url = 'https://www.linkedin.com/in/otamimi/'

obj = Scraper(driver, email, password)
obj.scrape_profile(linkedin_url)

# [] = for i obj.scrape_profile([i]).data

driver.quit()

var = obj.data
print(var)
