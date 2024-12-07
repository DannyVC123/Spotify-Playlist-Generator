import json
import requests
import webbrowser

from dotenv import load_dotenv
import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import random

from web_service import WebService
from Deprecated.spotify_client import SpotifyClient
from Deprecated.chatgpt_client import ChatGPTClient
from Deprecated.image_recognition import ImageRecognition

from track import Track
from artist import Artist
from playlist import Playlist

class Client:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')

        self.chatgpt_api_key = os.getenv('CHATGPT_API_KEY')
    
    def autorize(self):
        # https://developer.spotify.com/documentation/web-api/concepts/scopes
        scopes = [
            'user-read-recently-played',
            'playlist-modify-public',
            'playlist-modify-private'
        ]
        auth_url = (
            f'https://accounts.spotify.com/authorize?response_type=code&client_id={self.client_id}'
            f'&redirect_uri={self.redirect_uri}&scope={' '.join(scopes)}'
        )
        # print("Visit this URL to authorize the app:", auth_url)
        webbrowser.open(auth_url)

    def get_token(self, callback_url):
        # http://localhost:8080/?code=AQA9aROfylyTWis9bWy3oxgBiwFjcZlXRWMSCQj3hE1q78vLXs0qZTzoEOUPkoHrIVySwhBMLIsaK8JAFu1uCvU915EPp3lRoWnN7pw18Kff0dF2rzRzxuU-gEZ-weuo6wzkna_g2gQ44Ls3ohq7bSpYxf1Uw_8qtxaZtclTb5RGMUuTis4QXgL9gOFA7HHk8ijsuuDN0vDSQ3JQ5Myh5myMYle1eiQV0nCHOTA_UJLKhL6sxt1Gbfxyi56viHHi92gsjQI
        # callback_url = input('url >>> ')
        auth_code = None
        try:
            auth_code = callback_url.split("code=")[1]
        except:
            return None

        auth_str = f'{self.client_id}:{self.client_secret}'
        auth_base64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

        token_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }

        response = WebService.call(token_url, 'post', headers=headers, data=data)
        
        if response.status_code == 200:
            response_body = response.json()
            self.access_token = response_body['access_token']
            # refresh_token = response_body.get('refresh_token')  # Store for later use
            return self.access_token
        else:
            print("Error:", response.json())
            return None
    
    def init_external_clients(self):
        self.spotify_client = SpotifyClient(self.access_token)
        self.chatpgt_client = ChatGPTClient(self.chatgpt_api_key)
    
    ##############################
    #
    # generate ai playlist
    #
    ##############################
    def generate_ai_playlist(self, user_prompt, playlist_name, limit=10, public=False):
        # params_json = self.chatgpt_client.get_recommendations_json(user_prompt)
        # print(params_json)

        tracks_json = '''[
    {
        "title": "Spring Day",
        "artist": "BTS",
        "album": "You Never Walk Alone"
    },
    {
        "title": "Stay With Me",
        "artist": "Chanyeol, Punch",
        "album": "Guardian: The Lonely and Great God (Original Soundtrack)"
    },
    {
        "title": "Only Then",
        "artist": "Roy Kim",
        "album": "Begin Again 2"
    },
    {
        "title": "Love Scenario",
        "artist": "iKON",
        "album": "Return"
    },
    {
        "title": "LOSER",
        "artist": "BIGBANG",
        "album": "MADE"
    },
    {
        "title": "Eyes, Nose, Lips",
        "artist": "Taeyang",
        "album": "RISE"
    },
    {
        "title": "12월의 기적 (Miracles In December)",
        "artist": "EXO",
        "album": "Miracles in December"
    },
    {
        "title": "Beautiful",
        "artist": "Crush",
        "album": "Guardian: The Lonely and Great God (Original Soundtrack)"
    },
    {
        "title": "Breath",
        "artist": "Lee Hi",
        "album": "Seoulite"
    }
]'''
        return self.generate_playlist(user_prompt, playlist_name, limit, public)

    def generate_personalized_playlist(self, playlist_name, num_playlists=10, limit=10, public=False, include_private=False):
        playlists = self.spotify_client.get_playlists(num_playlists, include_private)

        tracks = []
        songs_per_playlist = 3
        for playlist in playlists:
            options = list(range(0, playlist.num_songs))
            random.shuffle(options)

            for offset in options[0:songs_per_playlist]:
                track = self.spotify_client.get_track_from_playlist(playlist.id, offset)
                tracks.append(track)
        
        user_prompt = 'Create a playlist based on the following songs:'
        for track in tracks:
            user_prompt += f'\n{track.name} by {track.artists[0].name}'
        
        return self.generate_playlist(user_prompt, playlist_name, limit, public)

    def generate_image_playlist(self, playlist_name, filename, limit=10, public=False):
        image_recognition = ImageRecognition()

        key_name = image_recognition.upload_image(filename)
        response = image_recognition.detect_labels(key_name)
        response_body = json.loads(response)

        user_prompt = 'Create a playlist based on the following words:'
        for label in response_body:
            user_prompt += f'{label['Name']}\n'
        
        return self.generate_playlist(user_prompt, playlist_name, limit, public)
    
    def generate_playlist(self, user_prompt, playlist_name, limit=10, public=False):
        tracks_json = self.chatpgt_client.get_recommendations_json(user_prompt, limit)
        tracks = self.spotify_client.get_all_tracks(tracks_json, limit)
        
        if tracks:
            playlist = self.spotify_client.create_playlist(playlist_name, public=public)
            playlist_url = self.spotify_client.populate_playlist(playlist, tracks)
        
        return (tracks, playlist_url)