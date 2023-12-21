import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기
df_building = pd.read_excel('kimgeuntae/year_deal_count/연도별_건축물거래.xlsx',header=10)
df_rand =  pd.read_excel('kimgeuntae/year_deal_count/연도별_순수토지거래.xlsx',header=10)
df_apt_deal = pd.read_excel('kimgeuntae/year_deal_count/연도별_아파트거래.xlsx',header=10)
df_apt = pd.read_excel('kimgeuntae/year_deal_count//연도별_아파트매매.xlsx',header=10)
df_home = pd.read_excel('kimgeuntae/year_deal_count/연도별_주택매매.xlsx',header=10)
df_rand_deal = pd.read_excel('kimgeuntae/year_deal_count/연도별_토지거래.xlsx',header=10)

# 6개의 데이터프레임 형태 같음 반복문을 통해 원하는 컬럼만 추출
categories = ['건축물거래','순수토지거래','아파트거래','아파트매매','주택매매','토지거래']
df_list = [df_building, df_rand,df_apt_deal,df_apt_deal,df_apt,df_home,df_rand_deal]
jejuDF = pd.DataFrame(columns=['거래형태','2013년','2014년','2015년','2016년','2017년','2018년','2019년','2020년','2021년','2022년'])
for i in range(len(categories)):
    jeju = df_list[i].iloc[296:]
    year_columns = ['Unnamed: 1']+[jeju.columns[i] for i in range(3,jeju.shape[1],2)]
    jeju = jeju[year_columns]
    cut_year_columns = jeju.columns[1:8]
    jeju.drop(cut_year_columns,inplace=True,axis=1)
    jeju.drop('2023년',axis=1,inplace=True)
    jeju.rename(columns={'Unnamed: 1':'거래형태'},inplace=True)
    jeju.iloc[0,0] = categories[i]
    jejuDF = pd.concat([jejuDF,jeju],axis=0)

# 데이터 정제
jejuDF = jejuDF.loc[296,:]
jejuDF.set_index('거래형태',inplace=True)
jejuDF.drop(index='아파트매매',axis=0,inplace=True)
jejuDF.loc['총 거래수'] = jejuDF.sum(axis=0)

# csv 파일로 저장
jejuDF.to_csv('kimgeuntae/year_deal_count/jeju_deal_count.csv')