# %%
import numpy as np
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from collections import OrderedDict
from sklearn import preprocessing
import scipy.cluster.hierarchy as spc
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.stats import spearmanr, pearsonr

# %%
data_csv = pd.read_csv("/Users/christianpederjacobsen/Dropbox/Mac/Desktop/leg/league_classifier/500_game_data.csv",index_col = False)
data_csv.drop(data_csv.columns[0],axis=1,inplace=True)
# %%
X = data_csv.iloc[:,0:-1]
X=(X-X.mean())/X.std()
Y = data_csv.iloc[:,-1]

# %%
fig = plt.figure(figsize=(10,6))
sns.heatmap(data_csv.corr(),vmin=-1, vmax=1)
plt.plot()
# %%
sns.clustermap(X.corr(), method="complete", cmap='RdBu', annot=True, 
               annot_kws={"size": 7}, vmin=-1, vmax=1, figsize=(15,12))
# %%
N,M = X.shape
print("Significant correlations between the Features and the Result of the game")
print()
for i in range(M):
    SCC,pvalue = pearsonr(X.iloc[:,i],Y)
    if pvalue < 0.05:
        print(X.columns[i],SCC,pvalue)

# Er gennemsnittet mellem korrelation significant forskellige

# %%
fig = plt.figure(figsize=(12,8))
data_csv.iloc[:,:].boxplot()
plt.xticks(rotation=90)
plt.show()
# %%
fig = plt.figure(figsize=(12,8))
data_csv.iloc[:,-1].hist()
plt.xticks(rotation=90)
plt.show()
# %%
winrate_data = pd.concat([data_csv.iloc[:,10:20], data_csv.iloc[:,-1]], axis=1)
# %%
fig = plt.figure(figsize=(12,8))
sns.violinplot(x="result",y="champ_winrate_red_mid",data=winrate_data, size=5, palette = 'colorblind')
plt.xticks(rotation=90)
plt.show()
# %%
sns.pairplot(winrate_data, hue="result", height = 2, palette = 'colorblind')

#%%
fig = plt.figure(figsize=(12,8))
data_csv_STD=(data_csv-data_csv.mean())/data_csv.std()
pd.plotting.parallel_coordinates(data_csv_STD, "result", color = ['red', 'blue'])
plt.xticks(rotation=90)
plt.show()
# %%
number_components = 5
pca = PCA(n_components=number_components)
components = pca.fit_transform(X)
principalDf = pd.DataFrame(data = components
             , columns = ["principal component {}".format(x+1) for x in range(number_components)])
finalDf = pd.concat([principalDf, Y], axis = 1)
# %%
colors = ["g","r"]
fig = plt.figure(figsize=(10,6))
for row in finalDf.to_numpy():
    plt.plot(row[0],row[1],label=int(row[-1]),color=colors[int(row[-1])],marker="s",linestyle="None")

handles, labels = plt.gca().get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())
plt.xlabel("PCA1")
plt.ylabel("PCA2")
plt.title("PCA analysis")
# %%
fig = plt.figure(figsize=(10,6))
variation_sum = 0
plt.plot(np.arange(1,len(pca.explained_variance_ratio_)+1),pca.explained_variance_ratio_)
plt.plot(np.arange(1,len(pca.explained_variance_ratio_)+1),np.cumsum(pca.explained_variance_ratio_))
plt.xlabel("Number of PC")
plt.ylabel("Variance explained")
plt.title("PCA analysis")
plt.show()
# %%
fig = plt.figure(figsize=(10,6))
colors = ["g","r","b","y","c"]
labels = ["PCA 1","PCA 2"]
bar_width = 0.2
for i in range(2):
    plt.bar(np.arange(1,1+X.shape[-1]) + bar_width*i,pca.components_[i,:],bar_width,color=colors[i],label=labels[i])
plt.xticks(np.arange(1,1+X.shape[-1]),list(data_csv.columns[:-1]),rotation=90)
plt.legend()
plt.xlabel("Features")
plt.ylabel("Component coeffecient")
plt.title("PCA components")
plt.show()
# %%
