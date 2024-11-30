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

    def __init__(self, authorization_token, user_id):
        self.authorization_token = authorization_token
        self.user_id = user_id
    
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
            print(tracks[-1])
        
        return tracks

    '''
    # https://developer.spotify.com/documentation/web-api/reference/get-recommendations
    def get_track_recommendations(self, tracks, num_songs=10):
        num_tracks = len(tracks)
        if num_tracks == 0:
            return []
        
        track_ids = [track.id for track in tracks]
        songs_per_call = round(num_songs / (len(track_ids) / 5))
        songs_left = num_songs
        
        recommended_tracks = []
        curr_track_id = 0
        while True:
            end_ind = min(curr_track_id + 5, len(track_ids))
            limit = min(songs_per_call, songs_left)
            seed_tracks = ','.join(track_ids[curr_track_id:end_ind])
            print(seed_tracks)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.authorization_token}'
            }
            url = f'https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks}&limit={limit}'
            
            response = WebService.call(url, 'get', headers=headers)
            response_body = response.json()
            if response.status_code not in [200, 201, 202, 204]:
                print(response.status_code)
                print(response_body)
                return None

            for track in response_body['tracks']:
                id      = track['id']
                name    = track['name']
                artists = []
                for artist in track['artists']:
                    artists.append(artist['name'])
                
                track = Track(id, name, artists)
                recommended_tracks.append(track)

            curr_track_id += 5
            songs_left -= limit
            if curr_track_id >= len(track_ids) or songs_left == 0:
                break
        
        for track in recommended_tracks:
            print(track)
        
        return recommended_tracks
    '''

    def get_artist(self, artist_name):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }
        url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=5'

        response = WebService.call(url, 'get', headers=headers)
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        
        artists = {}
        for item in response_body['artists']['items']:
            id      = item['id']
            name    = item['name']
            artists[name] = Artist(id, name.lower())
            print(f"Artist Name: {name}, Artist ID: {id}")
        
        closest_artist = difflib.get_close_matches(artist_name, artists.keys(), n=1)[0]
        print('closest', closest_artist)
        if closest_artist:
            return artists[closest_artist]
        else:
            return None
    
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
        id = first_track['id']
        name = first_track['name']
        
        artists = []
        for artist in first_track['artists']:
            artists.append(artist['name'])
        
        album_cover_url = None
        max_size = 0
        for image in first_track['album']['images']:
            size = image['height']
            if size > max_size:
                album_cover_url = image['url']
                max_size = size
        
        return Track(id, name, artists, album_cover_url)
    
    def get_all_tracks(self, params_json):
        tracks = []
        for track_json in params_json:
            name = track_json['title']
            artist = track_json['artist']
            tracks.append(self.get_track(name, artist))
        return tracks

    '''
    # https://developer.spotify.com/documentation/web-api/reference/get-recommendations
    def get_track_recommendations(self, params_json):
        print(params_json)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        params = json.loads(params_json)

        if 'seed_artists' in params:
            if len(params['seed_artists']) == 0:
                del params['seed_artists']
            else:
                artist_ids = []
                for artist_name in params['seed_artists']:
                    artist = self.get_artist(artist_name)
                    if not artist:
                        continue
                    print('----->', artist, artist.id)
                    artist_ids.append(artist.id)
                params['seed_artists'] = ','.join(artist_ids)
                print(params['seed_artists'])
        
        if 'seed_genres' in params:
            if len(params['seed_genres']) == 0:
                del params['seed_genres']
            else:
                params['seed_genres'] = ','.join(params['seed_genres'])
        
        # query_string = urllib.parse.urlencode(params, doseq=False)
        # print(query_string)

        print(params)

        url = f'https://api.spotify.com/v1/recommendations'
        
        response = WebService.call(url, 'get', headers=headers, params=params)
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None

        recommended_tracks = []
        for track in response_body['tracks']:
            id      = track['id']
            name    = track['name']

            artists = []
            for artist in track['artists']:
                artists.append(artist['name'])
            
            album_cover_url = None
            max_size = 0
            for image in track['album']['images']:
                size = image['height']
                if size > max_size:
                    album_cover_url = image['url']
                    max_size = size
            
            track = Track(id, name, artists, album_cover_url)
            recommended_tracks.append(track)

        for track in recommended_tracks:
            print(track)
        
        return recommended_tracks
    '''

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
        print(name)
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        id = response_body['id']
        return Playlist(id, name)

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