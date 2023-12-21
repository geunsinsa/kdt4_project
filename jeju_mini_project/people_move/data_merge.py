import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rc
rc('font', family='Malgun Gothic')

pure = pd.read_csv('kimgeuntae/people_move/pure_move.csv').T.rename(columns={0:'순 이동'}).reset_index()
jeju_in = pd.read_csv('kimgeuntae/people_move/total_move_in.csv').T.rename(columns={0:'전입'}).reset_index()
jeju_out = pd.read_csv('kimgeuntae/people_move/total_move_out.csv').T.rename(columns={0:'전출'}).reset_index()
populationDF = pd.merge(jeju_in,jeju_out,on='index')
populationDF = pd.merge(populationDF,pure, on='index')
populationDF.to_csv('kimgeuntae/people_move/jeju_population_move.csv')