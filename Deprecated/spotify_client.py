import json
import requests
import urllib

from dotenv import load_dotenv
import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import difflib

from web_service import WebService
from track import Track
from artist import Artist
from playlist import Playlist

class SpotifyClient:
    genres = [
        "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal", "bluegrass", "blues",
        "bossanova", "brazil", "breakbeat", "british", "cantopop", "chicago-house", "children", "chill", "classical",
        "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco",
        "disney", "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk", "forro", "french",
        "funk", "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar", "happy", "hard-rock",
        "hardcore", "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie",
        "indie-pop", "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin",
        "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore", "minimal-techno", "movies", "mpb", "new-age",
        "new-release", "opera", "pagode", "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep",
        "power-pop", "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton",
        "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes",
        "singer-songwriter", "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish",
        "synth-pop", "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
    ]

    def __init__(self, authorization_token):
        self.authorization_token = authorization_token
        self.user_id = self.get_user_id()
    
    ##############################
    #
    # user info
    #
    ##############################
    # https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    def get_user_id(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        url = 'https://api.spotify.com/v1/me'
        response = WebService.call(url, 'get', headers=headers)
        response_body = response.json()

        if response.status_code not in [200, 201, 202, 204]:
            print(response_body)
            return None
        
        return response_body['id']
    
    ##############################
    #
    # last played tracks
    #
    ##############################
    # https://developer.spotify.com/documentation/web-api/reference/get-recently-played
    def get_last_played_tracks(self, limit=10):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}'
        response = WebService.call(url, 'get', headers=headers)
        response_body = response.json()
        
        if response.status_code not in [200, 201, 202, 204]:
            print(response_body)
            return None

        tracks = []
        for item in response_body['items']:
            track_info  = item['track']
            track_id    = track_info['id']
            track_name  = track_info['name']

            artists = []
            for artist in track_info['artists']:
                artist_id = artist['id']
                artist_name = artist['name']
                artists.append(Artist(artist_id, artist_name))
            
            tracks.append(Track(track_id, track_name, artists))
        
        return tracks
    
    ##############################
    #
    # get tracks
    #
    ##############################
    def get_track(self, name, artist_name):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        url = f'https://api.spotify.com/v1/search?q={f'{name} {artist_name}'}&type=track&limit=1'

        response = WebService.call(url, 'get', headers=headers)
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        
        first_track = response_body['tracks']['items'][0]
        return self.get_track_from_dict(first_track)
    
    def get_track_from_dict(self, track_dict):
        id = track_dict['id']
        name = track_dict['name']
        
        artists = []
        for artist in track_dict['artists']:
            artists.append(Artist(artist['id'], artist['name']))
        
        album_cover_url = None
        max_size = 0
        for image in track_dict['album']['images']:
            size = image['height']
            if size > max_size:
                album_cover_url = image['url']
                max_size = size
        
        return Track(id, name, artists, album_cover_url)
    
    def get_all_tracks(self, tracks_json, limit):
        tracks = []
        track_ids = set()
        for track_json in tracks_json:
            name = track_json['title']
            artist = track_json['artist']

            track = self.get_track(name, artist)
            tracks.append(track)

            track_ids.add(track.id)
            if len(track_ids) == limit:
                break
        
        return tracks

    ##############################
    #
    # get user's playlists
    #
    ##############################
    def get_playlists(self, limit=10, include_private=False):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        playlists_per_call = 10
        url = f'https://api.spotify.com/v1/me/playlists?limit={playlists_per_call}'

        playlists = []
        while len(playlists) < limit:
            response = WebService.call(url, 'get', headers=headers)
            response_body = response.json()
            if response.status_code not in [200, 201, 202, 204]:
                print(response.status_code)
                print(response_body)
                return None
            
            for playlist_info in response_body['items']:
                public = playlist_info['public']
                if not public and not include_private:
                    continue

                id          = playlist_info['id']
                name        = playlist_info['name']
                num_songs   = playlist_info['tracks']['total']
                playlists.append(Playlist(id, name, num_songs))

                if len(playlists) == limit:
                    break
            
            if len(playlists) == limit or not response_body.get('next'):
                break
            else:
                url = response_body['next']
        
        return playlists
    
    def get_track_from_playlist(self, playlist_id, offset):
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=1&offset={offset}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        response = WebService.call(url, 'get', headers=headers)
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None

        track_info = response_body['items'][0]['track']
        return self.get_track_from_dict(track_info)

    ##############################
    #
    # create playlist
    #
    ##############################
    # https://developer.spotify.com/documentation/web-api/reference/create-playlist
    def create_playlist(self, name, description='My New Playlist', public=False):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'

        response = WebService.call(url, 'post', headers=headers, data=json.dumps(data))
        response_body = response.json()

        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        id = response_body['id']
        return Playlist(id, name, 0)

    # https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist
    def populate_playlist(self, playlist, tracks):
        track_uris = [track.get_uri() for track in tracks]
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        data = {
            'uris': track_uris
        }
        url = f'https://api.spotify.com/v1/playlists/{playlist.id}/tracks'

        response = WebService.call(url, 'post', headers=headers, data=json.dumps(data))
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        
        return f'https://open.spotify.com/playlist/{playlist.id}'