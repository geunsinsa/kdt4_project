import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font',family='AppleGothic')

# 공동주택, 단독주택 데이터 불러오기
share_home_DF = pd.read_excel('public_home_forigner.xlsx')
personal_home_Df = pd.read_excel('personal_home_forigner.xlsx')

# 컬럼명 변환 및 원하는 컬럼 추출해서 데이터프레임 재지정
share_home_DF.columns = ['도시', 'Unnamed: 1', 'Unnamed: 2', '공동주택 수', '(지분반영주택수)', '소유자수', '평균 공동주택 수', '(지분반영 1인당 평균소유주택수)']
share_home_DF = share_home_DF[['도시','공동주택 수','평균 공동주택 수']]
share_home_DF = share_home_DF.dropna(how='any')
personal_home_Df.columns = ['도시', 'Unnamed: 1', 'Unnamed: 2', '단독주택 수', '(지분반영주택수)', '소유자수', '평균 단독주택 수', '(지분반영 1인당 평균소유주택수)']
personal_home_Df = personal_home_Df[['도시','단독주택 수','평균 단독주택 수']]
personal_home_Df = personal_home_Df.dropna(how='any')
forigner_home_DF = pd.merge(personal_home_Df, share_home_DF, on='도시')

# 문자형 -> 숫자형 형변환
forigner_home_DF['단독주택 수'] = forigner_home_DF['단독주택 수'].str.replace(',','').astype(int)
forigner_home_DF['공동주택 수'] = forigner_home_DF['공동주택 수'].str.replace(',','').astype(int)
forigner_home_DF['평균 단독주택 수'] = forigner_home_DF['평균 단독주택 수'].astype(float)
forigner_home_DF['평균 공동주택 수'] = forigner_home_DF['평균 공동주택 수'].astype(float)

# 새로운 컬럼 생성 -> 제주의 외국인 소유 평균주택 수가 가장 많다는 인사이트 도출
forigner_home_DF['총 주택 수'] = forigner_home_DF['단독주택 수'] + forigner_home_DF['공동주택 수']
forigner_home_DF['총 평균 주택 수'] = round((forigner_home_DF['평균 단독주택 수'] * forigner_home_DF['단독주택 수'] + forigner_home_DF['평균 공동주택 수'].astype(float) * forigner_home_DF['공동주택 수']) / forigner_home_DF['총 주택 수'],2)

# 총 평균주택 수로 정렬
sort_DF = forigner_home_DF.sort_values('총 평균 주택 수',ascending=False)

# 시각화
plt.figure(figsize=(15,10))
sns.barplot(data=sort_DF, x='도시',y='총 평균 주택 수')
plt.title('지역별 외국인 소유 주택 평균 수',size=30)
plt.ylabel('평균 주택 수(인당)',size=20)
plt.xlabel('',size=0)
plt.xticks(size=20)
plt.yticks(size=20)
plt.ylim(0.9, 1.15)
plt.savefig('forigner_avg_home.png')