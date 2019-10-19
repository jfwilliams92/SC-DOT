import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# import geopandas as gpd 

def simple_func(x,y):
    return x + y


x = 1
y = 2

simple_func(x,y)
print('yes')


df = pd.read_csv("TrafficCounts2018.csv")

plt.scatter(df['Long,C,50'], df['Lat,C,50'], alpha=0.15, s=np.log(df['FactoredAA,N,24,5'].values), c=np.log(df['FactoredAA,N,24,5'].values))
plt.scatter(df['Long,C,50'], df['Lat,C,50'], alpha=0.15, s=np.log(df['FactoredAA,N,24,5'].values), c=np.log(df['FactoredAA,N,24,5'].values), cmap=plt.get_cmap("jet"))
df['FactoredAA,N,24,5'].hist()
df['log_FactoredAA'] = np.log(df['FactoredAA,N,24,5'].values)
df['log_FactoredAA'].hist(bins=50)
df['FactoredAA,N,24,5'].hist(bins=50)
df['log_FactoredAA'].hist(bins=50)