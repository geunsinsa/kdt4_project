import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='AppleGothic')

sqld_DF = pd.read_csv('sqlD.csv', usecols=['연도', '응시자 수'])

fig = plt.figure(figsize=(20, 20))  ## Figure 생성
fig.set_facecolor('white')  ## Figure 배경색 지정

plt.plot(sqld_DF['연도'], sqld_DF['응시자 수'], color='r',
         linestyle='-', marker='o',linewidth='10') ## 선 그래프 출력
plt.ylabel('응시자 수',size=30)
plt.xlabel('연도',size=30)
plt.xticks(size=30)
plt.yticks(size=30)
plt.title("SQLD 응시자 수 연도별 변화", fontsize=40)
plt.grid(visible=True)
plt.savefig('sqld.png')
plt.show()