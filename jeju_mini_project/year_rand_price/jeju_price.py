import pandas as pd

df_mama_dandok = pd.read_excel('kimgeuntae/year_rand_price/평균매매가격_단독.xlsx')
df_mama_apt = pd.read_excel('kimgeuntae/year_rand_price/지역별_아파트_매매_평균가격.xlsx')
df_mama_dasaedae = pd.read_excel('kimgeuntae/year_rand_price/평균매매가격_연립다세대.xlsx')

df_mama_dandok = df_mama_dandok.iloc[:,3:].rename(index={0:'단독_평균매매가격'})
df_mama_dandok = df_mama_dandok.T
df_mama_dandok = df_mama_dandok.iloc[12:df_mama_dandok.shape[1]-7]
df_mama_dandok.reset_index(inplace=True)

df_mama_apt = df_mama_apt.iloc[:,3:].rename(index={0:'아파트_평균매매가격'})
df_mama_apt = df_mama_apt.T
df_mama_apt = df_mama_apt.iloc[83:df_mama_apt.shape[1]-6]
df_mama_apt.reset_index(inplace=True)

df_mama_dasaedae = df_mama_dasaedae.iloc[:,3:].rename(index={0:'연립다세대_평균매매가격'})
df_mama_dasaedae = df_mama_dasaedae.T
df_mama_dasaedae = df_mama_dasaedae.iloc[12:df_mama_apt.shape[1]-7]
df_mama_dasaedae.reset_index(inplace=True)

df = pd.merge(df_mama_dandok,df_mama_dasaedae,left_on='index',right_on='index')
df = pd.merge(df,df_mama_apt,left_on='index',right_on='index')
df['index'] = df['index'].str.replace('월','')
df['index'] = df['index'].str.replace('년','-')
df['연'] = df['index'].str.split('-').str[0] 

group_year = round(df.groupby(by='연').mean(),1)
group_year['아파트_평균매매가격'] = group_year['아파트_평균매매가격']*100

group_year = group_year.astype(int)
group_year = group_year.T
group_year.to_csv('kimgeuntae/year_rand_price/jeju_rand_price.csv')