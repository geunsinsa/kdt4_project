import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas
url = "https://www.tiobe.com/tiobe-index/"
response = requests.get(url)
rank_html = BeautifulSoup(response.text, 'html.parser')

rank_list = []
rank_info = rank_html.select('#top20 > tbody')[0]
for i in range(0,20):
    rank = rank_info.select('tr')[i].select('td')[0].get_text()
    language = rank_info.select('tr')[i].select('td')[4].get_text()
    ratings = float(rank_info.select('tr')[i].select('td')[5].get_text().replace("%",''))
    rank_list.append([rank,language, ratings])

rankDF = pd.DataFrame(rank_list, columns=['Rank','Programming Language','Ratings(%)'])
rankDF.to_csv('rank_language.csv')