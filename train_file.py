import warnings
import numpy as np
import pandas as pd
from statistics import mean
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
import math
from sklearn.linear_model import LogisticRegression

warnings.simplefilter("ignore")

df_comb = pd.read_csv("Dataset/dis_sym_dataset_comb.csv") # Disease combination
df_norm = pd.read_csv("Dataset/dis_sym_dataset_norm.csv") # Individual Disease

X = df_comb.iloc[:, 1:]
Y = df_comb.iloc[:, 0:1]

"""Using **Logistic Regression (LR) Classifier** as it gives better accuracy compared to other classification models as observed in the comparison of model accuracies in Model_latest.py

Cross validation is done on dataset with cv = 5
"""

lr = LogisticRegression()
lr = lr.fit(X, Y)
scores = cross_val_score(lr, X, Y, cv=5)

X = df_norm.iloc[:, 1:]
Y = df_norm.iloc[:, 0:1]

# List of symptoms
dataset_symptoms = list(X.columns)
