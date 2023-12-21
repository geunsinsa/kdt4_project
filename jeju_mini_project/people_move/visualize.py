import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

population = pd.read_csv('jeju_population_move.csv', index_col=0)
plt.figure(figsize=(15,10))
sns.barplot(data=population, x='index',y='순 이동')
plt.title('제주도 순 이동(전입-전출) 변화',size=30)
plt.ylabel('이동 인구(명)',size=20)
plt.yticks(size=15)
# plt.ylim(40000,110000)
plt.xlabel('연도',size=15)
plt.xticks(size=20)
plt.ylim(0,16000)
plt.savefig('population_pure.png')

plt.figure(figsize=(15,10))
sns.lineplot(data=population, x='index',y='전입',color='blue',linewidth=5,legend=True)
sns.lineplot(data=population, x='index',y='전출', color='red',linewidth=5,legend=True)
plt.legend(labels=['전입','전출'])
plt.title('제주도 전입 전출 변화',size=30)
plt.ylabel('이동 인구(명)',size=20)
plt.yticks(size=15)
plt.xlabel('연도',size=15)
plt.xticks(size=20)
plt.ylim(70000,110000)
plt.grid(True)
plt.savefig('population_move.png')