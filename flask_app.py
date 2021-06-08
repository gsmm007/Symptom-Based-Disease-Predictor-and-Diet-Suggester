from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime
from nltk.corpus import wordnet 
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from itertools import combinations
from time import time
from collections import Counter
import operator
import math
from Treatment import diseaseDetail
from train_file import * 
import pickle
warnings.simplefilter("ignore")

"""Download resources required for NLTK pre-processing"""

import nltk
from train_file import *
import pdfkit

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask1'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskapp2'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def synonyms(term):
    synonyms = []
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.content,  "html.parser")
    try:
        container=soup.find('section', {'class': 'MainContentContainer'}) 
        row=container.find('div',{'class':'css-191l5o0-ClassicContentCard'})
        row = row.find_all('li')
        for x in row:
            synonyms.append(x.get_text())
    except:
        None
    for syn in wordnet.synsets(term):
        synonyms+=syn.lemma_names()
    return set(synonyms)

# utlities for pre-processing
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')
final_symp_new = []
dict_symp_tup= []

class RegisterForm(Form):
	firstname = StringField('firstname', [validators.Length(min=4, max=25)])
	lastname = StringField('lastname', [validators.Length(min=4, max=25)])
	email = StringField('email', [validators.Length(min=6, max=50)])
	password = PasswordField('password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

@app.route('/', methods=['GET', 'POST'])
def index():	
    if request.method == 'POST':
		# Get Form Fields
        email = request.form['login']
        password_candidate = request.form['login-password']
        print("Candidate Passsword")
        print(password_candidate)

		# Create cursor
        cur = mysql.connection.cursor()

		# Get user by username
        result = cur.execute("SELECT * FROM user WHERE email = %s", [email])
        print(result)
        if result > 0:
			# Get stored hash
            data = cur.fetchone()
            password = data['password']
            print(password)
			# Compare Passwords
            if (password_candidate == password) and request.method == 'POST':
                print("passwords matched")
				# Passed
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('home'))
            else:
                error = 'Invalid login'
                return render_template('index.html', error=error)
			# Close connection
            cur.close()
        else:
            error = 'User not registered'
            return render_template('index.html', error=error)

    return render_template('index.html')

@app.route('/index2.html',methods=['GET','POST'])
def index2():
    print(request.method)
    render_template('index2.html')
    form = RegisterForm(request.form)
    register()
    return render_template('index2.html',form = form)

@app.route('/main.html', methods =['GET', 'POST'])
def home():
    return render_template('main.html')

@app.route('/symp_check')
def sym():
    return render_template('symp_check.html')

@app.route('/your-disease', methods=['POST'])
def disease_pred():
    if request.method == 'POST':
        user_symptoms = str(request.form.get('symptoms_input')).lower().split(',')
        processed_user_symptoms = []
        for sym in user_symptoms:
            sym=sym.strip()
            sym=sym.replace('-',' ')
            sym=sym.replace("'",'')
            sym = ' '.join([lemmatizer.lemmatize(word) for word in splitter.tokenize(sym)])
            processed_user_symptoms.append(sym)

        """Pre-processing on symptoms entered by user is done."""

        # Taking each user symptom and finding all its synonyms and appending it to the pre-processed symptom string
        user_symptoms = []
        for user_sym in processed_user_symptoms:
            user_sym = user_sym.split()
            str_sym = set()
            for comb in range(1, len(user_sym)+1):
                for subset in combinations(user_sym, comb):
                    subset=' '.join(subset)
                    subset = synonyms(subset) 
                    str_sym.update(subset)
            str_sym.add(' '.join(user_sym))
            user_symptoms.append(' '.join(str_sym).replace('_',' '))
        # query expansion performed by joining synonyms found for each symptoms initially entered
        print("After query expansion done by using the symptoms entered")
        print(user_symptoms)

        # Loop over all the symptoms in dataset and check its similarity score to the synonym string of the user-input 
        # symptoms. If similarity>0.5, add the symptom to the final list
        found_symptoms = set()
        for idx, data_sym in enumerate(dataset_symptoms):
            data_sym_split=data_sym.split()
            for user_sym in user_symptoms:
                count=0
                for symp in data_sym_split:
                    if symp in user_sym.split():
                        count+=1
                if count/len(data_sym_split)>0.5:
                    found_symptoms.add(data_sym)
        found_symptoms = list(found_symptoms)

        """## **Prompt the user to select the relevant symptoms by entering the corresponding indices.**"""

        # Print all found symptoms
        print("Top matching symptoms from your search!")
        for idx, symp in enumerate(found_symptoms):
            print(idx,":",symp)
        global found_symptoms_list
        found_symptoms_list = found_symptoms 
    return render_template('disease_predictor.html', found_symptoms = found_symptoms)

@app.route('/your-disease2',methods =['POST'])
def disease_pred1():
    if request.method == 'POST':
        select_list = request.form.getlist('checkbox')
        print(select_list)
        dis_list = set()
        final_symp = [] 
        counter_list = []
        for symp_name in select_list:
            symp=symp_name
            final_symp.append(symp)
            dis_list.update(set(df_norm[df_norm[symp]==1]['label_dis']))
   
        for dis in dis_list:
            row = df_norm.loc[df_norm['label_dis'] == dis].values.tolist()
            row[0].pop(0)
            for idx,val in enumerate(row[0]):
                if val!=0 and dataset_symptoms[idx] not in final_symp:
                    counter_list.append(dataset_symptoms[idx])


        # Symptoms that co-occur with the ones selected by user              
        dict_symp = dict(Counter(counter_list))
        dict_symp_tup = sorted(dict_symp.items(), key=operator.itemgetter(1),reverse=True)  
        with open("test1.txt","wb") as fptr:
            pickle.dump(final_symp,fptr) 
        with open("test2.txt", "wb") as fp:   #Pickling
            pickle.dump(dict_symp_tup, fp)
        found_symptoms=[]
        count=0
        for tup in dict_symp_tup:
            count+=1
            found_symptoms.append(tup[0])
            if count%5==0 or count==len(dict_symp_tup):
                dict_symp_tup = dict_symp_tup[5:]
                with open("test2.txt", "wb") as fp:   #Pickling
                    pickle.dump(dict_symp_tup, fp)
                return render_template('disease_predictor2.html',found_symptoms = found_symptoms, dict_symp_tup = dict_symp_tup, final_symp = final_symp)
                select_list = request.form.getlist('checkbox2')
                print(len(select_list))
                for idx in select_list:
                    final_symp.append(found_symptoms[int(idx)])
                found_symptoms = []
    return render_template('disease_predictor2.html',found_symptoms = found_symptoms, dict_symp_tup = dict_symp_tup, final_symp=final_symp)

@app.route('/your-disease4',methods =['POST','GET'])
def fun():
    found_symptoms = []
    with open("test2.txt", "rb") as fp:   # Unpickling
        dict_symp_tup = pickle.load(fp)
    if request.method == 'POST':   
        select_list = request.form.getlist('checkbox2')
        if request.form.get('action') == "EXIT":
            with open("test1.txt", "rb") as fptr:
                old_sym = pickle.load(fptr)
            return render_template('disease_predictor3.html', final_symp_new = final_symp_new, old_sym = old_sym)
        if select_list[0] != "NoneofThese":
            for symp_name in select_list:
                final_symp_new.append(symp_name)
       
        print(dict_symp_tup)
        count = 0    
        for tup in dict_symp_tup:
            count+=1
            found_symptoms.append(tup[0])
            if count%5==0 or len(dict_symp_tup) < 5:
                dict_symp_tup = dict_symp_tup[5:]
                with open("test2.txt","wb") as fp:
                    pickle.dump(dict_symp_tup, fp)                
                return render_template('disease_predictor2.html',found_symptoms = found_symptoms)
            elif len(dict_symp_tup) < 5:
                return render_template('disease_predictor2.html', found_symptoms = found_symptoms)

@app.route('/your-disease5', methods = ['GET', 'POST'])
def confirm():
    return render_template('disease_predictor3.html')

@app.route('/prediction', methods =['GET', 'POST'])
def predict():
    if request.method == "POST":
        select_list1 = request.form.getlist('checkbox3')
        select_list2 = request.form.getlist('checkbox4')
        select_list = select_list1+select_list2
        sample_x = [0 for x in range(0,len(dataset_symptoms))]
        final_symp = select_list
        for val in select_list:
            print(val)
            sample_x[dataset_symptoms.index(val)]=1
        lr = LogisticRegression()
        lr = lr.fit(X, Y)
        prediction = lr.predict_proba([sample_x])

    
        k = 5
        diseases = list(set(Y['label_dis']))
        diseases.sort()
        topk = prediction[0].argsort()[-k:][::-1]
        print(f"\nTop {k} diseases predicted based on symptoms")
        topk_dict = {}
        for idx,t in  enumerate(topk):
            match_sym=set()
            row = df_norm.loc[df_norm['label_dis'] == diseases[t]].values.tolist()
            row[0].pop(0)
            for idx,val in enumerate(row[0]):
                if val!=0:
                    match_sym.add(dataset_symptoms[idx])
            prob = (len(match_sym.intersection(set(final_symp)))+1)/(len(set(final_symp))+1)
            prob *= mean(scores)
            topk_dict[t] = prob
        
        topk_index_mapping = {}
        topk_sorted = dict(sorted(topk_dict.items(), key=lambda kv: kv[1], reverse=True))
        disease_list = []
        j = 0
        for key in topk_sorted:
            prob = topk_sorted[key]*100
            disease_list.append(diseases[key])
            topk_index_mapping[j] = key
            j += 1
        with open("test3.txt", "wb") as fpdl: #pickling diseases
            pickle.dump(disease_list, fpdl)
        return render_template('prediction.html', topk_sorted = topk_sorted, topk_index_mapping = topk_index_mapping, diseases = diseases)

@app.route('/diet_suggester', methods = ['GET', 'POST'])
def diet():
    with open("test3.txt", "rb") as fpdl:
        disease_list = pickle.load(fpdl)
    disease = disease_list[0]
    suggested_diet = ''
    url='https://www.mtatva.com/en/disease/' + disease + '-treatment-diet-and-home-remedies/'
    req=requests.get(url)
    content=req.text
    soup=BeautifulSoup(content,'lxml')
    target = soup.find('h2',text='Food and Nutrition')
    for sib in target.find_next_siblings():
        if sib.name=="h2":
            break
        elif sib.text != None:
            suggested_diet += sib.text
            print(sib.text)
    print(suggested_diet)
    diet_split = suggested_diet.split('Foods to be avoided')
    diet1 = diet_split[0]
    diet1 = diet1.replace("Foods to be taken","")
    diet2 = diet_split[1]
    
    return render_template('diet_suggester.html',diet1 = diet1, diet2 = diet2) 

@app.route('/patient_details', methods = ['GET', 'POST'])
def details():
    return render_template('patient_details.html')
        
    
@app.route('/index2.html', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    print("reached_here" + request.method + form.email.data)
    if request.method == 'POST':
        fname = form.firstname.data
        lname = form.lastname.data
        email = form.email.data
        password = form.password.data
        print(fname)
		# Create cursor
        cur = mysql.connection.cursor()

		# Execute query
        cur.execute("INSERT INTO user(email,  password) VALUES(%s, %s)", (email, password))
        cur.execute("INSERT INTO user_inform(email,fname,lname) VALUES(%s, %s, %s)", (email, fname, lname))
		# Commit to DB
        mysql.connection.commit()

		# Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')
        #login()
        #flag = 1;
        return redirect(url_for('index'))

    return render_template('index.html', form=form)
if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
