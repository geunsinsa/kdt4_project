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


def Dfbyregion(cordinate, shopDF):
    subwayName = swDF.index
    busName = busDF.index
    shopName = shopDF.index
    schoolName = schoolDF.index

    
    nearNum = []
   
    subway_count = 0
    bus_count = 0
    shop_count = 0
    school_count = 0

    subway_sum = 0
    bus_sum = 0
    for name in subwayName:
        if geopy.distance.distance((cordinate[0],cordinate[1]),(swDF.loc[name][0],swDF.loc[name][1])) < 0.5:
            subway_count += 1
            subway_sum += swDF.loc[name,'평균유동인구']
    subway_sum = round(subway_sum,2)
    for name in busName:
        if geopy.distance.distance((cordinate[0],cordinate[1]), (busDF.loc[name]['위도'], busDF.loc[name]['경도'])) < 0.3:
            bus_count += 1
            bus_sum += busDF.loc[name,'하루평균유동인구']
    bus_sum = round(bus_sum,2)
    for idx in range(len(shopName)):
        if geopy.distance.distance((cordinate[0],cordinate[1]), (shopDF.iloc[idx][1], shopDF.iloc[idx][0])) < 0.3:
            shop_count += 1
    for i in range(len(schoolName)):
        if geopy.distance.distance((cordinate[0],cordinate[1]),(schoolDF.iloc[i,0], schoolDF.iloc[i,1])) < 1:
            school_count += 1
    total_sum = round(subway_sum + bus_sum,2)
    nearNum.append([shop_count, school_count, subway_count, subway_sum, bus_count, bus_sum, total_sum])

    
    return nearNum

print(Dfbyregion((35.8648,128.6080), shopDF))

