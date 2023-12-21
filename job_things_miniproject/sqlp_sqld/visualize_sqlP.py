import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc

rc('font', family='AppleGothic')

sqlP_DF = pd.read_csv('sqlP.csv', usecols=['연도', '응시자 수'])

fig = plt.figure(figsize=(20, 20))  ## Figure 생성
fig.set_facecolor('white')  ## Figure 배경색 지정

plt.plot(sqlP_DF['연도'], sqlP_DF['응시자 수'], color='r',
         linestyle='-', marker='o',linewidth='10') ## 선 그래프 출력
plt.ylabel('응시자 수',size=30)
plt.xlabel('연도',size=30)
plt.xticks(size=30)
plt.yticks(size=30)
plt.title("SQLP 응시자 수 연도별 변화", fontsize=40)
plt.grid(visible=True)
plt.savefig('sqlp.png')
plt.show()