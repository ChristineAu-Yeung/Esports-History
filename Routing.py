from flask import Flask, request
from flask_cors import CORS
import json
import League

app = Flask(__name__)
CORS(app)


@app.route('/set', methods=['POST'])
def setAPIKey():

    content = request.json
    APIkey = content['key']
    print(APIkey)
    if type(APIkey) is str and len(APIkey) > 0:
        with open('keyData.json', 'w') as jsonData:
            apiJson = {'apiKey': APIkey}
            json.dump(apiJson, jsonData)

    return 'Success'


@app.route('/')
def getGameData():
    summonerName = request.args.get("summonerName")
    apiKey = League.getAPIKey()
    numberMatches = 10
    if not summonerName:
        return 'Error'
    accountid = League.getAccountId(summonerName, apiKey)
    if accountid != None:
        matchInfo = League.getMatches(accountid, apiKey)
        statsList = League.getStatsofGames(
            summonerName, numberMatches, matchInfo, apiKey)
        return json.dumps(statsList)

    return 'Failed'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # main()
