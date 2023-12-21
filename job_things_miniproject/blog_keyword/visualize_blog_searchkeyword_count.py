import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

#빅데이터만 뽑아와서 시각화한 후 blog_keyword_count.png 로 저장
blogDF = pd.read_csv('blog_search_keyword_count.csv', index_col='Unnamed: 0')

year = list(blogDF.index)
bigdata_count = list(blogDF.빅데이터)

fig = plt.figure(figsize=(40, 20))  ## Figure 생성
fig.set_facecolor('white')  ## Figure 배경색 지정

colors = sns.color_palette('summer', len(year))  ## 바 차트 색상
plt.bar(year, bigdata_count, color=colors) ## 바차트 출력
plt.plot(year, bigdata_count, color='r',
         linestyle='--', marker='o') ## 선 그래프 출력
plt.ylabel('키워드 수',size=20)
plt.xlabel('연도',size=20)
plt.xticks(size=30)
plt.yticks(size=20)
plt.title("연도별 블로그 빅데이터 키워드 수", fontsize=40)
plt.savefig('blog_keyword_count.png')
plt.show()
