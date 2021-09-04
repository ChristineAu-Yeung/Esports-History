import requests
import json


def getAPIKey():
    with open('keyData.json') as jsonData:
        apiJson = json.load(jsonData)
        return apiJson["apiKey"]


def getUserInput():
    return input("Enter a summoner name: ")


def getNumberMatchesInput():
    return int(input("Enter the number of matches: "))


def getAccountId(summonerName, apiKey):

    summonerURL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + \
        summonerName+"?api_key="+apiKey
    summonerResponse = requests.get(summonerURL)
    if (summonerResponse.status_code != 200):
        print(
            f"Error in API call {summonerResponse.status_code} {summonerResponse.text}")
        return None
    summonerData = json.loads(summonerResponse.text)
    accountid = summonerData["accountId"]

    return accountid


def getMatches(accountid, apiKey):

    matchUrl = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + \
        accountid+"?api_key="+apiKey
    matchResponse = requests.get(matchUrl)
    if (matchResponse.status_code != 200):
        raise Exception("Get failed")
    matchInfo = json.loads(matchResponse.text)

    return matchInfo


def getStats(gameInfo, summonerName):
    gameData = json.loads(gameInfo.text)
    foundSummoner = False

    for i in range(0, len(gameData["participantIdentities"])):
        participantInfo = gameData["participantIdentities"][i]
        if(participantInfo["player"]["summonerName"] == summonerName):
            pid = participantInfo["participantId"]
            foundSummoner = True
            break
    if (foundSummoner == False):
        print("There are no games for this summoner")

    for i in range(0, len(gameData["participants"])):
        partData = gameData["participants"][i]
        partID = partData["participantId"]

        if(partID == pid):
            partGameInfo = gameData["participants"][pid-1]
            statsDict = {'winLose': partGameInfo["stats"]["win"],
                         'kills': partGameInfo["stats"]["kills"],
                         'deaths': partGameInfo["stats"]["deaths"],
                         'assists': partGameInfo["stats"]["assists"],
                         'role': partGameInfo["timeline"]["role"],
                         'lane': partGameInfo["timeline"]["lane"],
                         'champion': partGameInfo["championId"],
                         'gameMode': gameData["gameMode"],
                         'champInfo': getChampionInfo(partGameInfo["championId"])
                         }

    return statsDict


def getChampionInfo(championID):
    with open('Champions.json', 'r', encoding='utf-8') as json_file:
        championData = json.loads(json_file.read())
    for i in championData["data"]:
        if(str(championID) == str(championData["data"][i]["key"])):
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
        gameUrl = "https://na1.api.riotgames.com/lol/match/v4/matches/" + \
            str(matchid)+"?api_key="+apiKey
        gameInfo = requests.get(gameUrl)
        statsDict = getStats(gameInfo, summonerName)
        statsList.append(statsDict.copy())

    return statsList
