import requests 
import json
from bs4 import BeautifulSoup 
from exceptions import ResponseException
from userID import spotify_token, spotify_user_id

### CONSTANTS ####
MELON_URL = 'https://www.melon.com/chart/week/index.htm'
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
RANK = 50
HTML_TITLES_CLASS = "ellipsis rank01"
HTML_ARTISTS_CLASS = "ellipsis rank02"
HTML_DIV_CLASSIFIER = "div"
HTML_CLASS_CLASSIFIER = "class"

class CreatePlaylist:
    def __init__(self, playlist_name):
        self.all_song_info = {}
        self.uris = []
        self.playlist_id = self.create_spotify_playlist(playlist_name)
        self.get_melon_chart()
        self.add_songs()
    def get_melon_chart(self):
        req = requests.get(MELON_URL, headers = HEADER)
        # catch errorpip install  beautifulsoup4==4.8.1
        html = req.text
        parse = BeautifulSoup(html, 'html.parser')

        titles = parse.find_all(HTML_DIV_CLASSIFIER, {HTML_CLASS_CLASSIFIER: HTML_TITLES_CLASS}) 
        singers = parse.find_all(HTML_DIV_CLASSIFIER, {HTML_CLASS_CLASSIFIER: HTML_ARTISTS_CLASS}) 

        

        for i in range(RANK):
            title = titles[i].find('a').text
            artist = singers[i].find('a').text
            uri = self.get_spotify_uri(title,artist)
            if uri != '':
                self.uris.append(uri)

    def create_spotify_playlist(self, playlist_name):
        """Create A New Playlist"""
        request_body = json.dumps({
            "name": playlist_name,
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        # playlist id
        return response_json["id"]

    def get_spotify_uri(self, song_name, artist):
        """Search For the Song"""
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        if len(songs) != 0:
        # only use the first song
            uri = songs[0]["uri"]
            return uri
        return ''

    def add_songs(self):
        # add all songs into new playlist
        request_data = json.dumps(self.uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            self.playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            } )

        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json

if __name__ == "__main__":
    playlist = CreatePlaylist("MELON 50")