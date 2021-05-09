import requests
import json
import os

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def getAPIKey():
    with open('keyData.json') as jsonData:
        apiJson = json.load(jsonData)
        apiKey = apiJson["apiKey"]

    return apiKey

def getUserInput():

    summonerName = input("Enter a summoner name: ")
    numberMatches = int(input("Enter the number of matches: "))
    
    return summonerName, numberMatches

def getAccountId(summonerName, apiKey):

    summonerURL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+summonerName+"?api_key="+apiKey
    summonerResponse = requests.get(summonerURL)
    if (summonerResponse.status_code != 200):
        print("Error in API call", summonerResponse.status_code, summonerResponse.text)
        return None
    summonerData = json.loads(summonerResponse.text) 
    accountid = summonerData["accountId"] 
    
    return accountid

def getMatches(accountid, apiKey):

    matchUrl = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+accountid+"?api_key="+apiKey
    matchResponse = requests.get(matchUrl)
    matchInfo = json.loads(matchResponse.text)

    return matchInfo

def getStats(gameInfo, summonerName):

    data = json.loads(gameInfo.text)
    found = False

    for i in range(0, len(data["participantIdentities"])):
        partInfo = data["participantIdentities"][i]
        temp = partInfo["player"]["summonerName"]
        if(temp == summonerName):
            pid = partInfo["participantId"]
            found = True
            break;
    if (found == False):
        print("There are no games for this summoner")

    for i in range(0, len(data["participants"])):
        partData = data["participants"][i]
        partID = partData["participantId"]

        if(partID == pid):
            partGameInfo = data["participants"][pid-1]
            statsDict = {'winLose':partGameInfo["stats"]["win"], 
            'kills': partGameInfo["stats"]["kills"],
            'deaths' : partGameInfo["stats"]["deaths"],
            'assists': partGameInfo["stats"]["assists"],
            'role' : partGameInfo["timeline"]["role"],
            'lane' : partGameInfo["timeline"]["lane"],
            'champion' : partGameInfo["championId"],
            'gameMode' : data["gameMode"],
            'champInfo' : getChampionInfo(partGameInfo["championId"])
            }

    return statsDict

def getChampionInfo(championID):
    with open('Champions.json','r', encoding='utf-8') as json_file:
        championData = json.loads(json_file.read())
    for i in championData["data"]:
        if(str(championID) == str(championData["data"][i]["key"])):
            print(championData["data"][i]["image"]["full"])
            return(championData["data"][i]["image"]["full"])
    
            
def printOutput(statsList):

    for i in statsList: 
        if(i['winLose'] == True):
            print("Win")
        else: 
            print("Defeat")
        print("KDA:", i['kills'], i['deaths'], i['assists'])
        print("Role:", i['role'])
        print("Lane:", i['lane'])
        print("Champion:", i['champion'])
        print("Game Mode:", i['gameMode'])
        print()
        
def getStatsofGames(summonerName, numberMatches, matchInfo, apiKey):

    print(summonerName + "'s last " + str(numberMatches) + " games")
    print()
    statsList = []

    for i in range(numberMatches):
        match = matchInfo["matches"][i]
        matchid = match["gameId"]
        gameUrl = "https://na1.api.riotgames.com/lol/match/v4/matches/"+str(matchid)+"?api_key="+apiKey
        gameInfo = requests.get(gameUrl)
        statsDict = getStats(gameInfo, summonerName)
        statsList.append(statsDict.copy())

    return statsList

# def main():
#     apiKey = getAPIKey()
#     summonerName, numberMatches = getUserInput()
#     accountid = getAccountId(summonerName, apiKey)
#     if accountid != None:
#         matchInfo = getMatches(accountid, apiKey)
#         statsList = getStatsofGames(summonerName, numberMatches, matchInfo, apiKey)
#         printOutput(statsList)
    
@app.route('/')
def getGameData():
    summonerName = request.args.get("summonerName")
    apiKey = getAPIKey()
    numberMatches = 10
    if not summonerName: 
        return 'Error'
    accountid = getAccountId(summonerName, apiKey)
    if accountid != None:
        matchInfo = getMatches(accountid, apiKey)
        statsList = getStatsofGames(summonerName, numberMatches, matchInfo, apiKey)
        return json.dumps(statsList)
    return 'Failed'

if __name__ == '__main__':
    app.run()
    # main()

