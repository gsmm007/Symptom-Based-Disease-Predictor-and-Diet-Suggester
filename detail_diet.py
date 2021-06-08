from bs4 import BeautifulSoup
import requests
disease = 'influenza'
disease_dict = {'acne':'chapter428', 'alcoholism':'chapter429', 'allergies':'chapter430', 'anaemia':'chapter431', 'appendicitis':'chapter432', 'arteriosclerosis':'chapter433', 'asthma':'chapter434', 'arthritis':'chapter435', 'bronchitis':'chapter436', 'cataract':'chapter437', 'cirrhosis of the liver':'chapter438', 'colitis':'chapter439', 'conjunctivitis':'chapter440', 'constipation':'chapter441', 'diabetes':'chapter442', 'diarrhoea':'chapter443','dispepsia':'chapter444', 'eczema':'chapter445', 'epilepsy':'chapter446', 'fatigue':'chapter447', 'gall baldder disroders':'chapter448', 'gastritis':'chapter449', 'glaucoma':'chapter450', 'gout':'chapter451', 'heart disease':'chapter452', 'hypertension':'chapter453', 'influenza':'chapter454', 'insomnia':'chapter455', 'jaundice':'chapter456', 'kidney stones':'chapter457', 'low blood sugar':'chapter458', 'migraine':'chapter459', 'nepthritis':'chapter460', 'neurtis':'chapter461', 'obesity':'chapter462', 'peptic ulcer':'chapter463', 'piles':'chapter464', 'prostrate disorder':'chapter465', 'psoriasis':'chapter466', 'rheumatism':'chapter467', 'sexual disorders':'chapter468', 'sinusitis':'chapter469', 'stress':'chapter470', 'thinness':'chapter471', 'tuberculosis':'chapter472', 'varicose veins':'chapter473'}
key = disease
res = None
if key in disease_dict.keys():
    res = disease_dict[key]

detail_diet = ''
new_url = 'https://www.healthlibrary.com/book16_' + res +'.htm'
req=requests.get(new_url)
content=req.text

soup=BeautifulSoup(content,'html.parser')
print(soup.prettify())
target = soup.find('p',text='Causes')
print(target)
for sibling in target.find_next_siblings():
    if sibling.name=="p":
        break
    elif sibling.text != None:
        detail_diet += sibling.text
        print(sibling.text)
print(detail_diet)

	

