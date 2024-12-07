import json
import sys, os

from web_service import WebService
from track import Track
from artist import Artist
from playlist import Playlist

class SpotifyClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.user_id = self.get_user_id()

        # https://developer.spotify.com/documentation/web-api/concepts/api-calls
        # self.status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
    
    ##############################
    #
    # user info
    #
    ##############################
    # https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    def get_user_id(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        url = 'https://api.spotify.com/v1/me'

        status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        response = WebService.call(url, 'get', status_codes, headers=headers)
        response_body = response.json()

        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        
        return response_body['id']
    
    ##############################
    #
    # get tracks
    #
    ##############################
    def get_track(self, name, artist_name):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        url = f'https://api.spotify.com/v1/search?q={f'{name} {artist_name}'}&type=track&limit=1'

        status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        response = WebService.call(url, 'get', status_codes, headers=headers)
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
    # create playlist
    #
    ##############################
    # https://developer.spotify.com/documentation/web-api/reference/create-playlist
    def create_playlist(self, name, description='My New Playlist', public=False):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'

        status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        response = WebService.call(url, 'post', status_codes, headers=headers, data=json.dumps(data))
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
            'Authorization': f'Bearer {self.access_token}'
        }
        data = {
            'uris': track_uris
        }
        url = f'https://api.spotify.com/v1/playlists/{playlist.id}/tracks'

        status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        response = WebService.call(url, 'post', status_codes, headers=headers, data=json.dumps(data))
        response_body = response.json()
        if response.status_code not in [200, 201, 202, 204]:
            print(response.status_code)
            print(response_body)
            return None
        
        return f'https://open.spotify.com/playlist/{playlist.id}'