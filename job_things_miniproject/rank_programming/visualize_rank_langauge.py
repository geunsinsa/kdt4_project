import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

rankDf = pd.read_csv('rank_language.csv', usecols=['Rank', 'Programming Language', 'Ratings(%)'], index_col='Rank')

fig = plt.figure(figsize=(20,20))
fig.set_facecolor('white')
colors = sns.color_palette('crest', rankDf.shape[0])  ## 바 차트 색상
plt.bar(rankDf['Programming Language'],rankDf['Ratings(%)'], color=colors) ## 바차트 출력
plt.ylabel('사용률(%)',size=30)
plt.xlabel('언어',size=30)
plt.xticks(size=30,rotation=75)
plt.yticks(size=20)
plt.title("현재 프로그래밍 언어 사용률", fontsize=40)
plt.savefig('rank_language_bar.png')
plt.show()