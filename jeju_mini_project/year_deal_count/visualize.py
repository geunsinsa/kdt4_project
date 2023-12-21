import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

deal = pd.read_csv('jeju_deal_count.csv', index_col=0).T
deal = deal.reset_index()

plt.figure(figsize=(15,10))
sns.barplot(data=deal, x='index',y='총 거래수',palette="pastel", alpha=0.7 )
sns.lineplot(data=deal, x='index',y='총 거래수', color='red',linewidth=5 )
plt.title('제주도 총 부동산 거래 수',size=30)
plt.ylabel('거래 수',size=15)
plt.yticks(size=20)
plt.ylim(40000,110000)
plt.xlabel('연도',size=15)
plt.xticks(size=20)
plt.savefig('deal_graph.png')