import requests

class APIError(Exception):
    pass

class ClubSummary:
    def __init__(self, data):
        self.tag = data.get('tag')
        self.name = data.get('name')

class Player:
    def __init__(self, data):
        self.tag = data.get('tag')
        self.name = data.get('name')
        self.trophies = data.get('trophies')
        self.highest = data.get('highestTrophies')
        self.explevel = data.get('expLevel')
        self.club = ClubSummary(data.get('club, {}')) if data.get('club') else None

class Club:
    def __init__(self, data):
        self.tag = data.get('tag')
        self.name = data.get('name')
        self.trophies = data.get('trophies')
        self.required = data.get('requiredTrophies')
        self.type = data.get('type')

class BSWrapper:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.baseURL = 'https://api.brawlstars.com/v1'

    def request(self, endpoint):
        url = f"{self.baseURL}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.apiKey}',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers = headers)
        if response.status_code != 200:
            raise APIError(f'API Error: {response.status_code} - {response.text}')
        return response.json()
    
    def getplayer(self, tag):
        tag = tag.lstrip('#').upper()
        data = self.request(f'/players/%23{tag}')
        return Player(data)
    
    def getclub(self, tag):
        tag = tag.lstrip('#').upper()
        data = self.request(f'/clubs/%23{tag}')
        return Club(data)
    
    

