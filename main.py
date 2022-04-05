import sqlite3
import json
import os
if os.path.exists("ranking.db"):
  os.remove("ranking.db")
if os.path.exists("rounds.db"):
  os.remove("rounds.db")

conn = sqlite3.connect('rounds.db')
c = conn.cursor()

connR = sqlite3.connect('ranking.db')
cr = connR.cursor()


AUTO_MAX = 27
LIVE_MAX = 100
'''

Total weight = 100

'''
DRIVER_W = 0.15
DEFENSE_W = 0.05

OFFENSE_W = 0.7
AUTO_SCORE_W = 0.25
LIVE_SCORE_W = 0.5
HANGER_W = 0.25

RELIABILITY_W = 0.1
DAMAGE_SCORE_W = 0.9
SHOW_SCORE_W = 0.05
DIE_SCORE_W = 0.05



def printDB():
  print('\nPrinting database rounds.db...')
  c.execute("SELECT * FROM roundInfo")
  printList(c.fetchall())

  print('\nPrinting database ranking.db...')
  cr.execute("SELECT * FROM rankingInfo")
  printList(cr.fetchall())
def printList(myList):
  for i in myList:
    print(i)
def closePrgm():
  conn.commit()
  connR.commit()
  #printDB()
  c.close()
  conn.close()

  cr.close()
  connR.close()

def calcDriverW(aRow):
  driverW = int(aRow[33])
  print(driverW)
  return driverW

def calcDefenseW(aRow):
  defenseW = int(aRow[25])
  return defenseW

def calcOffenseW(aRow):
  autoScore = aRow[29]*AUTO_SCORE_W
  liveScore = aRow[30]*LIVE_SCORE_W
  hangerScore = aRow[31]*HANGER_W

  maxScore = 100*AUTO_SCORE_W + 100*LIVE_SCORE_W + 100*HANGER_W
  offenseW = ((autoScore + liveScore + hangerScore) / maxScore)*100
  return offenseW

def calcReliabilityW(aRow):
  damageW = (5-int(aRow[24]))*20*DAMAGE_SCORE_W
  showW = int(aRow[22])*SHOW_SCORE_W*100
  dieW = int(1-aRow[21])*DIE_SCORE_W*100

  maxScore = 100*DAMAGE_SCORE_W + 100*SHOW_SCORE_W + 100*DIE_SCORE_W
  reliabilityW = (((damageW + showW + dieW)/maxScore)*100)

  return reliabilityW

def updateRankings(teamNum):
    cr.execute("DELETE FROM rankingInfo where teamNum=?", (teamNum,))
    connR.commit()
    c.execute("SELECT * FROM roundInfo WHERE teamNum=?", (teamNum,))
    rows = c.fetchall()
    length = len(rows)
    cumDriver = 0
    cumDefense = 0
    cumOffense = 0
    cumReliability = 0
    for i in range(0,length):
      cumDriver = cumDriver + rows[i][32]
      cumDefense = cumDefense+rows[i][33]
      cumOffense = cumOffense+rows[i][34]
      cumReliability = cumReliability+rows[i][35]
    avgDriver =  int(( cumDriver/(100*length))*100)
    avgDefense = int((cumDefense/(100*length))*100)
    avgOffense = int((cumOffense/(100*length))*100)
    avgReliability = int((cumReliability/(100*length))*100)

    maxScore = 400
    avgOverall = int(((avgDriver + avgDefense + avgOffense + avgReliability)/maxScore)*100)

    cumDriverW = 0
    cumDefenseW = 0
    cumOffenseW = 0
    cumReliabilityW = 0
    for i in range(0,length):
      cumDriverW = cumDriverW + rows[i][32]
      cumDefenseW = cumDefenseW + rows[i][33]
      cumOffenseW = cumOffenseW + calcOffenseW(rows[i])
      cumReliabilityW = cumReliabilityW + calcReliabilityW(rows[i])

    avgDriverW =  int(( cumDriverW/(100*length))*100)
    avgDefenseW = int((cumDefenseW/(100*length))*100)
    avgOffenseW = int((cumOffenseW/(100*length))*100)
    avgReliabilityW = int((cumReliabilityW/(100*length))*100)

    maxScoreW = 100*DRIVER_W + 100*DEFENSE_W + 100*OFFENSE_W + 100*RELIABILITY_W
    avgOverallW = int(((avgDriverW + avgDefenseW + avgOffenseW + avgReliabilityW)/maxScoreW)*100)

    cr.execute(f"""INSERT INTO rankingInfo
                                      (teamNum,
                                       overall,
                                       driverScore,defenseScore,
                                       offenseScore,reliabilityScore,
                                       overallW,
                                       driverScoreW,defenseScoreW,
                                       offenseScoreW,reliabilityScoreW)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                                      (teamNum,
                                       avgOverall,
                                       avgDriver,avgDefense,
                                       avgOffense,avgReliability,
                                       avgOverallW,
                                       avgDriverW,avgDefenseW,
                                       avgOffenseW,avgReliabilityW))
#    cr.execute("SELECT * FROM roundInfo")

#    sortRanks = []
#    rows = cr.fetchall()
#    for i in range(0,len(rows)):
#      largest = 0
#      for j in range(0,

c.execute("""CREATE TABLE IF NOT EXISTS roundInfo(teamNum INTEGER,
                                            teamNumRound INTEGER,
                                            roundType INTEGER,
                                            scoutInit TEXT,
                                            matchNum TEXT,
                                            botType TEXT,
                                            autoHuman INTEGER,
                                            autoUpper INTEGER,
                                            autoLower INTEGER,
                                            taxiLoc INTEGER,
                                            didTaxi INTEGER,
                                            liveHuman INTEGER,
                                            liveUpper INTEGER,
                                            liveLower INTEGER,
                                            shots TEXT,
                                            low INTEGER,
                                            mid INTEGER,
                                            high INTEGER,
                                            trav INTEGER,
                                            term INTEGER,
                                            ground INTEGER,
                                            die INTEGER,
                                            show INTEGER,
                                            driver TEXT,
                                            damage TEXT,
                                            defense TEXT,
                                            comments TEXT,
                                            FIELD_WIDTH INTEGER,
                                            FIELD_HEIGHT INTEGER,
                                            autoScore INTEGER,
                                            liveScore INTEGER,
                                            hangerScore INTEGER,
                                            drivingScore INTEGER,
                                            defenseScore INTEGER,
                                            offenseScore INTEGER,
                                            reliabilityScore INTEGER
                                            )""")
conn.commit()

cr.execute("""CREATE TABLE IF NOT EXISTS rankingInfo(teamNum INTEGER,
                                            overall INTEGER,
                                            driverScore INTEGER,
                                            defenseScore INTEGER,
                                            offenseScore INTEGER,
                                            reliabilityScore INTEGER,
                                            overallW INTEGER,
                                            driverScoreW INTEGER,
                                            defenseScoreW INTEGER,
                                            offenseScoreW INTEGER,
                                            reliabilityScoreW INTEGER
                                            )""")

conn.commit()


lines = []
file = open("CollectData.txt")
for line in file:
  lines.append(line.strip())

for i in range(1,len(lines)-1):
  if i*2 > len(lines):
    break;
#  print(lines[(i*2)-2])
#  print(lines[(i*2)-1])


#collecting = True
#while collecting:
  
#  break;
  
  #firstVersion = input('Waiting FIRST version...')
  #secondVersion = input('Waiting SECOND version..')
  #firstVersion = '{"version":1,"preData":{"scoutInit":"Js","teamNum":"1678","matchNum":"5","roundType":"Quals","botType":"Red 3"},"autoData":{"taxiLoc":{"x":-1,"y":-1},"didTaxi":false,"upper":5,"lower":0,"human":0,"shots":[6]},"liveData":{"upper":27,"lower":0,"human":0,"shots":[{"x":345,"y":250},{"x":393,"y":98}]}}'
  #secondVersion = '{"version":2,"postData":{"low":0,"mid":0,"trav":0,"high":0,"ground":true,"term":true,"die":false,"foul":0,"show":true,"driver":"4","damage":"1","defense":"2","comments":"Shot around tarmac a lot"},"FIELD_WIDTH":736,"FIELD_HEIGHT":351.9}'
  firstVersion = lines[(i*2)-2]
  secondVersion = lines[(i*2)-1]
  if (firstVersion == "stop"):
    collecting = False
    break
  print((i*2)-2)
  match1 = json.loads( firstVersion)
  match2 = json.loads(secondVersion)
  teamNum = int(match1["preData"]["teamNum"])
  
  c.execute("SELECT * FROM roundInfo WHERE teamNum=?", (teamNum,))

  rows = c.fetchall()
  teamNumRound = len(rows)
  roundType = match1["preData"]["roundType"]
  scoutInit = match1["preData"]["scoutInit"]
  matchNum = match1["preData"]["matchNum"]
  botType = match1["preData"]["botType"]

  autoHuman = match1["autoData"]["human"]
  autoUpper = match1["autoData"]["upper"]
  autoLower = match1["autoData"]["lower"]
  taxiLoc = str(match1["autoData"]["taxiLoc"])
  didTaxi = 0 if match1["autoData"]["didTaxi"] == "false" else 1
  
  liveHuman = match1["liveData"]["human"]
  liveUpper = match1["liveData"]["upper"]
  liveLower = match1["liveData"]["lower"]
  shots = str(match1["liveData"]["shots"])

  low = match2["postData"]["low"]
  mid = match2["postData"]["mid"]
  high = match2["postData"]["high"]
  trav = match2["postData"]["trav"]
  ground = 0 if match2["postData"]["ground"] == "false" else 1
  term = 0 if match2["postData"]["term"] == "false" else 1
  die = 0 if match2["postData"]["die"] == "false" else 1
  foul = match2["postData"]["foul"]
  show = 0 if match2["postData"]["show"] == "false" else 1
  
  driver = int(match2["postData"]["driver"])
  damage = int(match2["postData"]["damage"])
  defense = int(match2["postData"]["defense"])
  comments = str(match2["postData"]["comments"])

  FIELD_WIDTH = int(match2["FIELD_WIDTH"])
  FIELD_HEIGHT = int(match2["FIELD_HEIGHT"])

  
  driverScore  =  (driver-1)*25 # range is [1,5]; we need [0,4] -> [0,100]
  defenseScore = (defense-1)*(25)

  taxiScore = 4
  if taxiScore == 0:
    taxiScore = 0
  # we need to revise human functionality (whether or not we should keep it)
  autoRawScore = autoHuman*0 + autoUpper*4 + autoLower*2 + taxiScore
  autoScore = int((autoRawScore/ AUTO_MAX) * 100)

  liveRawScore = liveHuman*2 + liveUpper*2 + liveLower
  liveScore = (liveRawScore/LIVE_MAX) * 100
  hangerScore = 0 #4, 6,, 10, 15
  if trav == 1:
    hangerScore = 15
  elif trav == 2:
    hangerScore = 0
  else:
    if high == 1:
      hangerScore = 10
    elif high == 2:
      hangerScore = 0
    else:  
      if mid == 1:
        hangerScore = 6
      elif mid == 2:
        hangerScore = 0
      else:
        if low == 1:
          hangerScore = 4

  hangerPercScore = 0
  if hangerScore == 4:
    hangerPercScore = 25
  elif hangerScore == 6:
    hangerPercScore = 40
  elif hangerScore == 10:
    hangerPercScore = 65
  elif hangerScore == 15:
    hangerPercScore = 100
  
  offenseScore = int(((autoScore + liveScore + hangerPercScore) / 300)*100)

  showScore = 100
  if show == 0:
    showScore = 0

  damageScore  =  ((5-damage)-1)*25
  dieScore = 100 #100 is desired. means not die
  if die == 1: # means die == true, really bad
    die = 0


  reliabilityScore = int(((showScore + damageScore + dieScore) / 300)*100)

  c.execute(f"""INSERT INTO roundInfo
                                      (teamNum,teamNumRound,roundType,scoutInit,matchNum,botType,
                                      autoHuman,autoUpper,autoLower,taxiLoc,didTaxi,
                                      liveHuman,liveUpper,liveLower,shots,
                                      low,mid,high,trav,term,ground,die,show,
                                      driver,damage,defense,comments,FIELD_WIDTH,FIELD_HEIGHT,
                                      autoScore,liveScore,hangerScore,
                                      drivingScore,defenseScore,offenseScore,reliabilityScore)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                      (teamNum,teamNumRound,roundType,scoutInit,matchNum,botType,
                                      autoHuman,autoUpper,autoLower,taxiLoc,didTaxi,
                                      liveHuman,liveUpper,liveLower,shots,
                                      low,mid,high,trav,term,ground,die,show,
                                      driver,damage,defense,comments,FIELD_WIDTH,FIELD_HEIGHT,
                                      autoScore,liveScore,hangerPercScore,
                                      driverScore,defenseScore,offenseScore,reliabilityScore))

  updateRankings(int(teamNum))
  collecting = False
  
closePrgm()












