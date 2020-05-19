import requests
from urllib.parse import urlencode

from .utils import unix_to_date

class Game:
    def __init__(self, igdb_json, detailed = False):
        if detailed:
            self.age_ratings = igdb_json.get('age_rating', None)
            self.critic_rating= igdb_json.get('aggregated_rating', None)
            self.genres = igdb_json.get('genres', None)
            self.platforms = igdb_json.get('platforms', None)
            self.videos = igdb_json.get('videos', None)
            self.websites = igdb_json.get('websites', None)
            self.time_to_beat = igdb_json.get('time_to_beat', None)
        
        self.id = igdb_json.get('id', None)
        self.name = igdb_json.get('name', None)
        self.cover = igdb_json.get('cover', None)
        self.release_date = igdb_json.get('first_release_date', None)

    def __repr__(self):
        return self.name
        

class GameClient:
    def __init__(self, key):
        self.base_url = 'https://api-v3.igdb.com/'
        self.header = {'user-key' : key, 'Accept' :'application/json'}

    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        payload = {'search': search_string, 'limit': 30, 'fields': "name,cover,first_release_date,id,popularity"}
        url = f"{self.base_url}games/?{urlencode(payload)}"
        response = requests.get(url, headers=self.header)
        if response.status_code != 200:
            raise ValueError(f'Error searching the API\n{response.text}')
        result = []
        response = response.json()

        for x in response:
            game = Game(x)
            if game.cover:
                url = f"{self.base_url}covers/"
                r = requests.get(url, headers = self.header, params = {'fields': f'*; where id = {game.cover}'})
                r = r.json()
                r = r[0]
                game.cover = r['url']
            if game.release_date:
                game.release_date = unix_to_date(game.release_date)
            result.append(game) 

        return result



    def retrieve_game_by_id(self, game_id):
        """ 
        Use to obtain a Game object representing the game identified by
        the supplied igdb_id
        """
        payload = {'fields' : f"*; where id = {game_id}" }
        url = f"{self.base_url}games/"
        response = requests.get(url,headers = self.header, params = payload)
        data = response.json()
        game = Game(data[0], detailed=True)
        if game.cover:
            url = f"{self.base_url}covers/"
            r = requests.get(url, headers = self.header, params = {'fields': f'*; where id = {game.cover}'})
            r = r.json()
            r = r[0]
            game.cover = r['url']
        if game.release_date:
            game.release_date = unix_to_date(game.release_date)
        else: game.release_date = "Unknown"
        if game.genres:
            genre_list = []
            for g in game.genres:
                url = f"{self.base_url}genres/"
                r = requests.get(url, headers = self.header, params = {'fields': f'name; where id = {g}'})
                r = r.json()
                r = r[0]
                genre_list.append(r['name'])
            game.genres = genre_list
        else: game.genres = "Unknown"

        if game.platforms:
            platform_list = []
            for p in game.platforms:
                url = f"{self.base_url}platforms/"
                r = requests.get(url, headers = self.header, params = {'fields': f'*; where id = {p}'})
                r = r.json()
                r = r[0]
                platform_list.append(r['name'])
            game.platforms = platform_list
        else: game.platforms = "Unknown"

        if game.websites:
            website_list = []
            for w in game.websites:
                url = f"{self.base_url}websites/"
                r = requests.get(url, headers = self.header, params = {'fields': f'*; where id = {w}'})
                r = r.json()
                r = r[0]
                website_list.append(r['url'])
            game.websites = website_list

        if game.time_to_beat:
            url = f"{self.base_url}time_to_beats/"
            r = requests.get(url, headers = self.header, params = {'fields' : f' *; where id = {game.time_to_beat}'})
            r = r.json()
            if r:
                r = r[0]
                game.time_to_beat = str(r['normally']/60) + " Hours"
            else : game.time_to_beat =  "Unknown"
        else : game.time_to_beat = "Unknown"

        return game


## -- Example usage -- ###
if __name__=='__main__':
    import os

    client = GameClient(os.environ.get('IGDB_API_KEY'))

    games = client.search("assassins")