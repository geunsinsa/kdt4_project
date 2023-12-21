import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font',family='AppleGothic')

# trend.csv 파일 데이터프레임으로 가져오기
trend = pd.read_csv('trend.csv')
trend.Scala = trend.Scala.str.replace('<1','0').astype(int)

# 4가지 keyword에 대한 데이터를 한 그래프에 저장
fig = plt.figure(figsize=(30, 20))  ## Figure 생성
fig.set_facecolor('white')  ## Figure 배경색 지정
ax = fig.add_subplot(1,1,1)

ax.plot(trend['월'], trend['Python'],
        markersize=10, color='blue',linewidth='10',label='Python')
ax.plot(trend['월'], trend['R'],
        markersize=10, color='red',linewidth='10',label='R')
ax.plot(trend['월'], trend['Scala'],
        markersize=10, color='green',linewidth='5',label='Scala')
ax.plot(trend['월'], trend['Julia'],
        markersize=10, color='yellow',linewidth='5',label='Julia')

ax.legend(loc='best',fontsize=30)

ax.set_title("시간 흐름에 따른 언어 관심도 변화",size=60)
ax.set_xlabel('시간',size=30)
ax.set_ylabel('관심도',size=30)

ax.set_xticklabels(trend['월'], rotation=90)
plt.yticks(size=30)
plt.gca().axes.xaxis.set_visible(False)

# 그래프 저장하기
plt.savefig('language_trend.png')
plt.show()