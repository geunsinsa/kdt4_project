import pandas as pd
import geopy.distance

# 데이터프레임 만들기 => 구별 스타벅스만 가져오면 된다
swDF = pd.read_csv('subway/final_subway.csv',index_col='역명')
busDF = pd.read_csv('bus/final_bus.csv', index_col='정류소명')
busDF = busDF.drop('Unnamed: 0', axis=1)
schoolDF = pd.read_csv('school/school.csv',encoding='cp949', index_col='학교명')


# 함수 변수로 사용할 것은 구별 스타벅스의 명 
starbucksDF = pd.read_csv('starbucks/region_divide/fourGu_22.csv', index_col='매장명')
shopDF = pd.read_csv('shop/new_shop_22.csv', index_col='상호명')
shopDF = shopDF.drop('Unnamed: 0', axis=1)

# 4개로 나눈 지역구들의 매장 주변 (지하철, 버스, 학교, 상가) 수를 분석하는 함수
def Dfbyregion(sbDF, shopDF):
    subwayName = swDF.index
    starbucksName = sbDF.index
    busName = busDF.index
    shopName = shopDF.index
    schoolName = schoolDF.index

    
    nearNum = []
    for sname in starbucksName:
        subway_count = 0
        bus_count = 0
        shop_count = 0
        school_count = 0

        subway_sum = 0
        bus_sum = 0
        for name in subwayName:
            if geopy.distance.distance((sbDF.loc[sname][0],sbDF.loc[sname][1]),(swDF.loc[name][0],swDF.loc[name][1])) < 0.5:
                subway_count += 1
                subway_sum += swDF.loc[name,'평균유동인구']
        subway_sum = round(subway_sum,2)
        for name in busName:
            if geopy.distance.distance((sbDF.loc[sname][0],sbDF.loc[sname][1]), (busDF.loc[name]['위도'], busDF.loc[name]['경도'])) < 0.3:
                bus_count += 1
                bus_sum += busDF.loc[name,'하루평균유동인구']
        bus_sum = round(bus_sum,2)
        for idx in range(len(shopName)):
            if geopy.distance.distance((sbDF.loc[sname][0],sbDF.loc[sname][1]), (shopDF.iloc[idx][1], shopDF.iloc[idx][0])) < 0.3:
                shop_count += 1
        for i in range(len(schoolName)):
            if geopy.distance.distance((sbDF.loc[sname][0],sbDF.loc[sname][1]),(schoolDF.iloc[i,0], schoolDF.iloc[i,1])) < 1:
                school_count += 1
        total_sum = round(subway_sum + bus_sum,2)
        nearNum.append([shop_count, school_count, subway_count, subway_sum, bus_count, bus_sum, total_sum])

    d1 = pd.DataFrame(nearNum,columns=['인접_상가수','인접_학교수','인접_지하철역수','하루평균유동인구_지하철','인접_버스정류장수','하루평균유동인구_버스','하루평균유동인구_대중교통'],index=starbucksName)
    appendDf = sbDF.join(d1)
    
    return appendDf

Dfbyregion(starbucksDF, shopDF).to_csv('datas_By_region_year/analyze_fourGu_22.csv')


