import warnings
import numpy as np
import pandas as pd
from statistics import mean
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
import math
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier,GradientBoostingClassifier

warnings.simplefilter("ignore")

df_comb = pd.read_csv("Dataset/dis_sym_dataset_comb.csv") # Disease combination
df_norm = pd.read_csv("Dataset/dis_sym_dataset_norm.csv") # Individual Disease

X = df_comb.iloc[:, 1:]
Y = df_comb.iloc[:, 0:1]

"""Using **Logistic Regression (LR) Classifier** as it gives better accuracy compared to other classification models as observed in the comparison of model accuracies in Model_latest.py

Cross validation is done on dataset with cv = 5
"""
from sklearn import preprocessing
from sklearn.feature_selection import VarianceThreshold
var_thres=VarianceThreshold(threshold=0)
var_thres.fit(x_train)
print(len(x_train.columns[var_thres.get_support()]))
constant_columns = [column for column in x_train.columns
                    if column not in x_train.columns[var_thres.get_support()]]

print(len(constant_columns))
x_train.drop(constant_columns,axis=1)
bg2 = BaggingClassifier(LogisticRegression(), oob_score = True)
bg2.fit(x_train,y_train)
scores_bg2 = cross_val_score(bg2, X,Y, cv=5)


X = df_norm.iloc[:, 1:]
Y = df_norm.iloc[:, 0:1]

# List of symptoms
dataset_symptoms = list(X.columns)
