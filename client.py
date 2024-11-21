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

from web_service import WebService
from spotify_client import SpotifyClient
from track import Track
from playlist import Playlist

class Client:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
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
        auth_code = callback_url.split("code=")[1]

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
            access_token = response_body.get('access_token')
            # refresh_token = response_body.get('refresh_token')  # Store for later use
            return access_token
        else:
            print("Error:", response.json())
            return None

'''
def exchange_code_for_tokens(auth_code):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = WebService.call(url, 'post', headers=headers, data=data)
    response_body = response.json()
    if response.status_code not in [200, 201, 202, 204]:
        print(response_body)
        return None, None

    access_token = response_body['access_token']
    refresh_token = response_body['refresh_token']
    return access_token, refresh_token

def refresh_access_token(refresh_token):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = WebService.call(url, 'post', headers=headers, data=data)
    response_body = response.json()
    if response.status_code not in [200, 201, 202, 204]:
        print(response_body)
        return None
    
    new_access_token = response_body['access_token']
    return new_access_token
'''

'''
auth_url = generate_authorization_url()
webbrowser.open(auth_url)
access_token = get_token()

# access_token, refresh_token = exchange_code_for_tokens(auth_code)

# spotify_client = None
# if access_token and refresh_token:
    # spotify_client = SpotifyClient(access_token, user_id)

# new_access_token = refresh_access_token(refresh_token)
spotify_client = SpotifyClient(access_token, user_id)

# last_played_tracks = spotify_client.get_last_played_tracks()

params_json = """{
  "limit": 10,
  "seed_artists": ["fuslie", "lilypichu"]
}
"""
recommended_tracks = spotify_client.get_track_recommendations(params_json)

if recommended_tracks:
    playlist = spotify_client.create_playlist('lily and fuslie chat gpt playlist')
    playlist_url = spotify_client.populate_playlist(playlist, recommended_tracks)
    webbrowser.open(playlist_url)
'''
