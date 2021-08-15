# %%
import numpy as np
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import SGDClassifier
# %%

data_csv = pd.read_csv("/Users/christianpederjacobsen/Dropbox/Mac/Desktop/leg/league_classifier/500_game_data.csv",index_col = False)
data_csv.drop(data_csv.columns[0],axis=1,inplace=True)
# %%
X = data_csv.iloc[:,0:-1]
X=(X-X.mean())/X.std()
Y = data_csv.iloc[:,-1]

X = X.to_numpy()
Y = Y.to_numpy()


X_train, X_test, y_train, y_test = X[:400], X[400:], Y[:400], Y[400:]
# %%
from sklearn.linear_model import SGDClassifier
sgd_clf = SGDClassifier(random_state=42)
sgd_clf.fit(X_train, y_train)
# %%
sgd_clf.predict(X)
# %%
from sklearn.model_selection import cross_val_score
cross_val_score(sgd_clf, X_train, y_train, cv=3, scoring="accuracy")
# %%
from sklearn.base import BaseEstimator
class Never5Classifier(BaseEstimator): 
    def fit(self, X, y=None):
        pass
    def predict(self, X):
        return np.zeros((len(X), 1), dtype=bool)


never_blå_sejr = Never5Classifier()
cross_val_score(never_blå_sejr, X_train, y_train, cv=3, scoring="accuracy")
# %%
from sklearn.model_selection import cross_val_predict
y_train_pred = cross_val_predict(sgd_clf, X_train, y_train, cv=3)
# %%
from sklearn.metrics import confusion_matrix
confusion_matrix(y_train, y_train_pred)
# %%
from sklearn.metrics import precision_score, recall_score
print("The classifier is only correct:",precision_score(y_train, y_train_pred),"percent of the time")
print("It only detects",recall_score(y_train, y_train_pred),"Blå sejr")

# %%
from sklearn.metrics import f1_score
f1_score(y_train, y_train_pred)
# %%
from sklearn.linear_model import LogisticRegression
LR = LogisticRegression(random_state=0).fit(X_train, y_train)

# %%
y_train_pred = cross_val_predict(LR, X_train, y_train, cv=3)

# %%
f1_score(y_train,y_train_pred)
# %%
from sklearn.feature_selection import RFE
LR = LogisticRegression(random_state=0)
backward_selection = RFE(LR,verbose=1,n_features_to_select=10, step=1)
backward_selection = backward_selection.fit(X_train,y_train)
# %%
backward_selection.support_
# %%
X_relevant_features = X_train[:,backward_selection.ranking_ == 1]
# %%
LR = LogisticRegression(random_state=0).fit(X_relevant_features,y_train)
y_train_pred = cross_val_predict(LR, X_relevant_features, y_train, cv=3)

# %%
f1_score(y_train,y_train_pred)

# %%
X_test_relevant = X_test[:,backward_selection.ranking_ == 1]
y_train_pred = cross_val_predict(LR, X_test_relevant, y_test, cv=3)

# %%
f1_score(y_train,y_train_pred)
