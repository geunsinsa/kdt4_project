class PlayerInfoGet:
    def __init__(self,team,name):
        self.name = name
        self.team = team

    def getDB(self):
        import mariadb as mdb
        conn_params = {"host":'127.0.0.1',
                       'port':3306,
                       'user':'geunsinsa',
                       'password':'geunsinsa',
                       'database':'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        q_basic_info = 'select * from tbl_basicInfo where 소속구단 = ? and  이름 = ? '
        q_season_record = "SELECT r.* FROM tbl_basicInfo AS b JOIN tbl_recordInfo AS r ON CONCAT(b.이름,' ', REPLACE(b.생년월일,'-','')) = r.이름 WHERE b.소속구단 = ? and b.이름 = ?"

        cur.execute(q_basic_info,(self.team,self.name))
        plBasicInfo = cur.fetchall()

        cur.execute(q_season_record,(self.team,self.name))
        plSeasonRecord= cur.fetchall()
        cur.close()
        conn.close()
        return plBasicInfo, plSeasonRecord

    def makeDataFrame(self):
        import pandas as pd
        import numpy as np
        plBasicInfo, plSeasonRecord = self.getDB()

        plBasicInfo = plBasicInfo[0]
        basicInfoDF = pd.DataFrame([plBasicInfo])
        basicInfoDF.columns = ['기타','이름','영문명','소속','포지션','등번호','국적','키','몸무게','생년월일','이미지주소']
        basicInfoDF = basicInfoDF.drop(columns=['기타'])
        basicInfoDF['이미지주소'] = basicInfoDF['이미지주소'].apply(lambda x: '/static/pl'+x)

        recordList = []
        for season in plSeasonRecord:
            recordList.append(list(season[2:]))
        recordInfoDF = pd.DataFrame(recordList)
        recordInfoDF.columns = ['연도','리그','소속','출장','득점','도움','골킥','코너킥','오프사이드','슈팅','파울','실점','경고','퇴장']
        recordInfoDF = recordInfoDF.groupby(by='연도').agg('sum').reset_index()

        return basicInfoDF, recordInfoDF

    def makeTotalRecord(self):
        import pandas as pd
        _, recordInfoDF = self.makeDataFrame()

        totalReccord = recordInfoDF[recordInfoDF.columns[2:]]
        totalReccord =  pd.DataFrame(totalReccord.sum())
        return totalReccord

class TeamInfoGet:
    def __init__(self):
        pass
    @staticmethod
    def getTeamName():
        import mariadb as mdb
        conn_params = {"host":'127.0.0.1',
                       'port':3306,
                       'user':'geunsinsa',
                       'password':'geunsinsa',
                       'database':'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        q_team_name = 'select distinct(소속구단) from tbl_basicInfo'

        cur.execute(q_team_name)
        teamName = cur.fetchall()

        teamList = []
        for name in teamName:
            teamList.append(name[0])

        cur.close()
        conn.close()

        return teamList

    @staticmethod
    def getTeamInPlayerName(team):
        import mariadb as mdb
        conn_params = {"host": '127.0.0.1',
                       'port': 3306,
                       'user': 'geunsinsa',
                       'password': 'geunsinsa',
                       'database': 'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        q_team_in_plyaer_name = 'select 포지션, 배번, 이름 from tbl_basicInfo where 소속구단 = ?'
        cur.execute(q_team_in_plyaer_name,([team]))

        teamPlayerList = []
        for name in cur.fetchall():
            teamPlayerList.append(name[:3])

        teamPlayerList = sorted(teamPlayerList,key=lambda x: (('FW', 'MF', 'DF', 'GK').index(x[0]),x[1]))
        cur.close()
        conn.close()

        return teamPlayerList


class TextCosine:
    def __init__(self,text):
        self.text = text

    def textconcat(self):
        import mariadb as mdb
        import pandas as pd
        conn_params = {"host": '127.0.0.1',
                       'port': 3306,
                       'user': 'geunsinsa',
                       'password': 'geunsinsa',
                       'database': 'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        query1 = 'select 이름, 소속구단, 정보 from tbl_text'
        cur.execute(query1)
        textList = cur.fetchall()

        query2 = 'select 이름,소속구단,포지션,배번,국적, 키,몸무게, 생년월일 from tbl_basicInfo'
        cur.execute(query2)
        basicInfoList = cur.fetchall()

        cur.close()
        conn.close()

        textDF = pd.DataFrame(textList,columns=['이름','소속','정보'])
        textDF.loc[textDF['이름'] == '김정호','정보'] = '강원 fc 김정호 골키퍼 등번호 25번 국적 한국 키 184cm 몸무게 82kg 생년월일 1998년 4월 7일'

        for idx in range(len(textList)):
            appendText = f'이름은 {basicInfoList[idx][0]} 소속팀은 {basicInfoList[idx][1]} 포지션은 {basicInfoList[idx][2]} 등번호는 {basicInfoList[idx][3]}번 국적은 {basicInfoList[idx][4]} 키는 {basicInfoList[idx][5]}cm 몸무게는 {basicInfoList[idx][6]}kg 생일은 {basicInfoList[idx][7]}'
            textDF.loc[idx,'정보'] = appendText + textDF.loc[idx,'정보']
        return textDF

    def cosineVector(self):
        import pandas as pd
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from konlpy.tag import Okt

        def get_playerList(guess, cosine_sim):
            idx = indices[guess]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:4]  # self.text 자신을 제외하고 유사도가 높은 상위 3개 선택
            player_indices = [i[0] for i in sim_scores]
            return textDF[['이름', '소속']].iloc[player_indices]

        guess = self.text
        textDF = self.textconcat()

        okt = Okt()
        textDF.loc[len(textDF)] = ['정답', '정답', guess]

        textDF['정보'] = textDF['정보'].apply(lambda x: ' '.join(okt.nouns(x)))
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(textDF['정보'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        indices = pd.Series(textDF.index, index=(textDF['정보'])).drop_duplicates()

        return get_playerList(textDF.loc[len(textDF)-1,'정보'], cosine_sim)

    def getPlayerInfo(self):
        import mariadb as mdb
        import pandas as pd

        predPlayer = self.cosineVector()
        conn_params = {"host": '127.0.0.1',
                       'port': 3306,
                       'user': 'geunsinsa',
                       'password': 'geunsinsa',
                       'database': 'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        infoList = []
        query1 = "select *  from tbl_basicInfo where 이름 = ? and 소속구단 = ?"
        for idx in predPlayer.index:
            cur.execute(query1,(predPlayer.loc[idx,'이름'],predPlayer.loc[idx,'소속']))
            infoList.append(cur.fetchall()[0])

        a = []

        for info in infoList:
            info = list(info)
            info[-1] = '/static/pl' + info[-1]
            a.append(info)
        cur.close()
        conn.close()

        return a

class GetSimilarPlayer:
    def __init__(self,name,team):
        self.name = name
        self.team = team

    def getSimilarPlayerData(self):
        from sqlalchemy import text, create_engine
        import pandas as pd
        from sklearn.neighbors import NearestNeighbors
        from sklearn.preprocessing import StandardScaler
        # 선수 세부기록 로딩
        engine = create_engine('mysql+pymysql://geunsinsa:geunsinsa@127.0.0.1/k_league')
        connection = engine.connect()
        query = text("select * from tbl_concat2023")
        result = connection.execute(query)
        detailDF = pd.DataFrame(result,columns=result.keys()).drop(columns=['index'])


        # 유사한 선수를 찾을 선수의 경기 세부기록 선택 & 같은 포지션 (예: target_player)
        target_player = detailDF[(detailDF['이름'] == self.name) & (detailDF['소속구단'] == self.team)]
        target_position = target_player['포지션'].values[0]
        target_record = target_player[detailDF.columns[7:]].values

        # NearestNeighbors 모델 초기화

        same_postion = detailDF[detailDF['포지션'] == target_position]
        scale = StandardScaler()
        feature = scale.fit_transform(same_postion[same_postion.columns[7:]])
        target_record = scale.transform(target_record)

        k = 4  # 원하는 이웃의 수
        model = NearestNeighbors(n_neighbors=k)

        # 특정 선수의 데이터를 모델에 학습
        model.fit(feature)

        # 유사한 선수를 찾기
        _, indices = model.kneighbors(target_record)

        similaPlayerlist = []
        for idx in indices[0]:
            similaPlayerlist.append(same_postion.iloc[idx, :].values)

        similaPlayerDF = pd.DataFrame(similaPlayerlist, columns=detailDF.columns)

        return similaPlayerDF

    def getStat(self):
        import pandas as pd
        similaPlayerDF = self.getSimilarPlayerData()

        if similaPlayerDF.iloc[0, 2] != 'GK':
            offense = pd.DataFrame(similaPlayerDF['득점'] + similaPlayerDF['도움'], columns=['공격']).set_index(
                similaPlayerDF['이름'])

            dribleP = round(similaPlayerDF['드리블성공'] / similaPlayerDF['드리블시도'], 1)
            if dribleP.isnull().sum() != 0:
                dribleP = dribleP.fillna(0)
            drible = pd.DataFrame(dribleP + similaPlayerDF['탈압박'], columns=['드리블']).set_index(similaPlayerDF['이름'])

            groundP = round(similaPlayerDF['경합 지상성공'] / similaPlayerDF['경합 지상시도'], 1)
            if groundP.isnull().sum() != 0:
                groundP = groundP.fillna(0)
            skyP = round(similaPlayerDF['경합 공중성공'] / similaPlayerDF['경합 공중시도'], 1)
            if skyP.isnull().sum() != 0:
                skyP = skyP.fillna(0)
            physical = pd.DataFrame(groundP + skyP, columns=['피지컬']).set_index(similaPlayerDF['이름'])

            defense = pd.DataFrame(
                similaPlayerDF['클리어링'] + similaPlayerDF['인터셉트'] + similaPlayerDF['차단'] + similaPlayerDF['획득'] +
                similaPlayerDF['블락'], columns=['수비']).set_index(similaPlayerDF['이름'])

            passP = round(similaPlayerDF['패스성공'] / similaPlayerDF['패스시도'], 1)
            if passP.isnull().sum() != 0:
                passP = passP.fillna(0)
            fowardP = round(similaPlayerDF['전방 패스성공'] / similaPlayerDF['전방 패스시도'], 1)
            if fowardP.isnull().sum() != 0:
                fowardP = fowardP.fillna(0)
            backP = round(similaPlayerDF['후방 패스성공'] / similaPlayerDF['후방 패스시도'], 1)
            if backP.isnull().sum() != 0:
                backP = backP.fillna(0)
            rowP = round(similaPlayerDF['횡패스성공'] / similaPlayerDF['횡패스시도'], 1)
            if rowP.isnull().sum() != 0:
                rowP = rowP.fillna(0)
            ofP = round(similaPlayerDF['공격지역패스성공'] / similaPlayerDF['공격지역패스시도'], 1)
            if ofP.isnull().sum() != 0:
                ofP = ofP.fillna(0)
            dfP = round(similaPlayerDF['수비지역패스성공'] / similaPlayerDF['수비지역패스시도'], 1)
            if dfP.isnull().sum() != 0:
                dfP = dfP.fillna(0)
            midP = round(similaPlayerDF['중앙지역패스성공'] / similaPlayerDF['중앙지역패스시도'], 1)
            if midP.isnull().sum() != 0:
                midP = midP.fillna(0)
            longP = round(similaPlayerDF['롱패스성공'] / similaPlayerDF['롱패스시도'], 1)
            if longP.isnull().sum() != 0:
                longP = longP.fillna(0)
            middleP = round(similaPlayerDF['중거리패스성공'] / similaPlayerDF['중거리패스시도'], 1)
            if middleP.isnull().sum() != 0:
                middleP = middleP.fillna(0)
            shortP = round(similaPlayerDF['숏패스성공'] / similaPlayerDF['숏패스시도'], 1)
            if shortP.isnull().sum() != 0:
                shortP = shortP.fillna(0)
            totalPass = round((passP + fowardP + backP + rowP + ofP + dfP + midP + longP + middleP + shortP) / 10, 3)
            totalPass = pd.DataFrame(totalPass, columns=['패스']).set_index(similaPlayerDF['이름'])

            playerStat = pd.concat([offense, drible, physical, defense, totalPass], axis=1)
            playerStat = round(playerStat/playerStat.iloc[0],2)
            playerStat = playerStat.reset_index()
        else:
            passP = round(similaPlayerDF['패스성공'] / similaPlayerDF['패스시도'], 1)
            if passP.isnull().sum() != 0:
                passP = passP.fillna(0)
            fowardP = round(similaPlayerDF['전방 패스성공'] / similaPlayerDF['전방 패스시도'], 1)
            if fowardP.isnull().sum() != 0:
                fowardP = fowardP.fillna(0)
            backP = round(similaPlayerDF['후방 패스성공'] / similaPlayerDF['후방 패스시도'], 1)
            if backP.isnull().sum() != 0:
                backP = backP.fillna(0)
            rowP = round(similaPlayerDF['횡패스성공'] / similaPlayerDF['횡패스시도'], 1)
            if rowP.isnull().sum() != 0:
                rowP = rowP.fillna(0)
            ofP = round(similaPlayerDF['공격지역패스성공'] / similaPlayerDF['공격지역패스시도'], 1)
            if ofP.isnull().sum() != 0:
                ofP = ofP.fillna(0)
            dfP = round(similaPlayerDF['수비지역패스성공'] / similaPlayerDF['수비지역패스시도'], 1)
            if dfP.isnull().sum() != 0:
                dfP = dfP.fillna(0)
            midP = round(similaPlayerDF['중앙지역패스성공'] / similaPlayerDF['중앙지역패스시도'], 1)
            if midP.isnull().sum() != 0:
                midP = midP.fillna(0)
            longP = round(similaPlayerDF['롱패스성공'] / similaPlayerDF['롱패스시도'], 1)
            if longP.isnull().sum() != 0:
                longP = longP.fillna(0)
            middleP = round(similaPlayerDF['중거리패스성공'] / similaPlayerDF['중거리패스시도'], 1)
            if middleP.isnull().sum() != 0:
                middleP = middleP.fillna(0)
            shortP = round(similaPlayerDF['숏패스성공'] / similaPlayerDF['숏패스시도'], 1)
            if shortP.isnull().sum() != 0:
                shortP = shortP.fillna(0)
            totalPass = round((passP + fowardP + backP + rowP + ofP + dfP + midP + longP + middleP + shortP) / 10, 3)
            totalPass = pd.DataFrame(totalPass, columns=['빌드업']).set_index(similaPlayerDF['이름'])
            quickness = pd.DataFrame(
                similaPlayerDF['클리어링'] + similaPlayerDF['인터셉트'] + similaPlayerDF['차단'] + similaPlayerDF['획득'] +
                similaPlayerDF['블락'], columns=['처리(순발력)']).set_index(similaPlayerDF['이름'])
            stability = pd.DataFrame(similaPlayerDF['볼미스'] + similaPlayerDF['파울'], columns=['불안감']).set_index(
                similaPlayerDF['이름'])
            playerStat = pd.concat([quickness, totalPass, stability], axis=1)
            print(playerStat)
            playerStat = round(playerStat/playerStat.iloc[0],2).reset_index()
        return playerStat

    def concatBirthIMG(self):
        similaPlayerDF = self.getSimilarPlayerData()
        import mariadb as mdb
        conn_params = {"host": '127.0.0.1',
                       'port': 3306,
                       'user': 'geunsinsa',
                       'password': 'geunsinsa',
                       'database': 'k_league'}

        conn = mdb.connect(**conn_params)
        cur = conn.cursor()

        imgList = []
        for idx in range(4):
            name, team = similaPlayerDF.iloc[idx, 0], similaPlayerDF.iloc[idx, 1]
            query1 = 'select `이미지 주소` from tbl_basicInfo where 이름 = ? and 소속구단 = ?'
            cur.execute(query1, (name, team))
            result = cur.fetchall()
            imageLink = '/static/pl' + result[0][0]
            imgList.append(imageLink)
        cur.close()
        conn.close()
        similaPlayerDF['주소'] = imgList
        similaPlayerDF = similaPlayerDF[['이름', '소속구단', '포지션', '배번', '키', '몸무게', '생년월일', '주소','출전시간(분)', '득점', '도움',
       '슈팅', '유효 슈팅', '차단된슈팅', '벗어난슈팅', 'PA내 슈팅', 'PA외 슈팅', '오프사이드', '프리킥',
       '코너킥', '스로인', '드리블시도', '드리블성공', '패스시도', '패스성공', '키패스', '전방 패스시도',
       '전방 패스성공', '후방 패스시도', '후방 패스성공', '횡패스시도', '횡패스성공', '공격지역패스시도',
       '공격지역패스성공', '수비지역패스시도', '수비지역패스성공', '중앙지역패스시도', '중앙지역패스성공', '롱패스시도',
       '롱패스성공', '중거리패스시도', '중거리패스성공', '숏패스시도', '숏패스성공', '크로스시도', '크로스성공',
       '탈압박', '경합 지상시도', '경합 지상성공', '경합 공중시도', '경합 공중성공', '태클시도', '태클성공',
       '클리어링', '인터셉트', '차단', '획득', '블락', '볼미스', '파울', '피파울', '경고', '퇴장']]
        return similaPlayerDF


from sklearn.ensemble import Rand