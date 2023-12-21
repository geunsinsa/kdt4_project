from flask import Flask, render_template
from plyaerInfo.kLeagueApp.getInfo import TeamInfoGet, PlayerInfoGet, TextCosine, GetSimilarPlayer

app = Flask(__name__)


@app.route('/')
def startPage():
    return render_template('startPage.html')

@app.route('/search')
def searchPage():
    return render_template('homePage.html')

@app.route('/threePlayer/<text>')
def show3Players(text):
    three_players = TextCosine(text).getPlayerInfo()
    return render_template('threePlayer.html',three_players=three_players, text=text)

@app.route('/team')
def firstPage():
    team_info_getter = TeamInfoGet()
    team_names = team_info_getter.getTeamName()
    return render_template('firstPage.html', team_names=team_names)

@app.route('/team/<teamname>')
def showPlayers(teamname):
    team_player_name = TeamInfoGet().getTeamInPlayerName(teamname)
    return render_template('teamPlayer.html', teamname=teamname, team_player_name=team_player_name)

@app.route('/team/<teamname>/<player>')
def showPlayerInfo(teamname, player):
    info = PlayerInfoGet(teamname,player)
    basicInfo, record = info.makeDataFrame()
    record = record.sort_index(ascending=False)
    totalRecord = info.makeTotalRecord()
    return render_template('player.html',team=teamname,name=player,basicInfo=basicInfo,record=record,lenRecord=len(record),totalRecord=totalRecord)

@app.route('/team/similar/<teamname>/<player>')
def show_similar_player(teamname,player):
    simlar = GetSimilarPlayer(player,teamname)
    playerStat = simlar.getStat()
    playerRecord = simlar.concatBirthIMG()
    playerStat_dict = playerStat.to_dict('records')  # '이름' 열 포함하여 사전 형태로 변환
    stat_labels = list(playerStat.columns)  # 모든 열 이름
    stat_labels.remove('이름')  # '이름' 제거
    print(playerStat_dict)
    return render_template('similar.html',teamname=teamname, player=player, playerStat=playerStat_dict, playerRecord=playerRecord, stat_labels=stat_labels)


@app.route('/team/<teamname>/<player>/<text>')
def showPlayerInfo2(teamname, player,text):
    info = PlayerInfoGet(teamname,player)
    basicInfo, record = info.makeDataFrame()
    record = record.sort_index(ascending=False)
    totalRecord = info.makeTotalRecord()
    return render_template('player2.html',team=teamname,name=player,basicInfo=basicInfo,record=record,lenRecord=len(record),totalRecord=totalRecord,text=text)

@app.route('/team/similar/<teamname>/<player>/<text>')
def show_similar_playe2(teamname,player,text):
    simlar = GetSimilarPlayer(player,teamname)
    playerStat = simlar.getStat()
    playerRecord = simlar.concatBirthIMG()
    playerStat_dict = playerStat.to_dict('records')  # '이름' 열 포함하여 사전 형태로 변환
    stat_labels = list(playerStat.columns)  # 모든 열 이름
    stat_labels.remove('이름')  # '이름' 제거
    print(playerStat_dict)
    return render_template('similar2.html',text=text,teamname=teamname, player=player, playerStat=playerStat_dict, playerRecord=playerRecord, stat_labels=stat_labels)



if __name__ == '__main__':
    app.run(debug=True)  # Listen on all available network interfaces



