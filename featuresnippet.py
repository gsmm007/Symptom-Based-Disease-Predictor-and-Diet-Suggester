import csv
from selenium import webdriver
import random
import time
from bs4 import BeautifulSoup
import requests

delay_seconds = random.randint(100,500)/100

chromedriver = "/snap/bin/chromium.chromedriver"
driver = webdriver.Chrome(chromedriver)

queries = ['Influenza diet','Common Cold diet']


for item in queries:
	google_url = "https://www.google.com/search?q="+item
	driver.get(google_url)
	time.sleep(delay_seconds)
	r = requests.get(google_url)
	html_doc = r.text
	soup = BeautifulSoup(google_url,'lxml')

	for s in soup.body.div.findAll(id="res"):
		print(reached_here)
		s = s.text.replace('Search ResultsFeatured snippet from the web','').split(">")[0]
		ns = s.replace('Search ResultsWebSearch','NoSnippet:')
		data = item,ns
		print(data)




