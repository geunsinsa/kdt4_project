import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

price = pd.read_csv('jeju_rand_price.csv', index_col=0).T
price = price.reset_index()
col_name = price.columns
image_name = ['home','share_home','apt']
for col in range(1, len(col_name)):
    plt.figure(figsize=(15,10))
    sns.lineplot(x=price['index'], y=price[col_name[col]],color='red',linewidth=5)
    plt.grid(True)
    plt.title(f"{col_name[col]} 변화",size=30)
    plt.ylabel('평균 거래액(천)',size=15)
    plt.yticks(size=20)
    plt.xlabel('')
    plt.xticks(size=20)
    plt.savefig(f'{image_name[col-1]}.png')