from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait

url = "https://www.google.com/search?q=influenza+diet"

chromedriver = "/snap/bin/chromium.chromedriver"
driver = webdriver.Chrome(chromedriver)

driver.get(url)

snippet = wait(driver, 60).until(lambda driver: driver.find_element_by_css_selector("div.res"))
print(snippet.text)
