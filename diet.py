from bs4 import BeautifulSoup
import requests

def diet(disease):
	url='https://www.mtatva.com/en/disease/' + disease + '-treatment-diet-and-home-remedies/'
	req=requests.get(url)
	content=req.text
	soup=BeautifulSoup(content,'lxml')
	target = soup.find('h2',text='Food and Nutrition')
	for sib in target.find_next_siblings():
		if sib.name=="h2":
        		break
		elif sib.text != None:
       	 		print(sib.text)

	
disease = input("enter disease: ")
print(diet(disease))


#Integrate with SymptomSuggestion.py





