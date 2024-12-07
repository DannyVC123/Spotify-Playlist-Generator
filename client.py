import json
import requests
import boto3
import webbrowser

from dotenv import load_dotenv
import uuid
import os
import base64

from configparser import ConfigParser

from web_service import WebService

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

        self.setup_aws()
    
    def setup_aws(self):
        # s3
        config_file = 'playlist-config.ini'

        s3_profile = 's3readwrite'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        boto3.setup_default_session(profile_name=s3_profile)

        configur = ConfigParser()
        configur.read(config_file)
        self.bucket_name = configur.get('s3', 'bucket_name')
        self.region_name = configur.get(s3_profile, 'region_name')

        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(self.bucket_name)

        # endpoint
        self.api_endpoint = configur.get('client', 'webservice')
    
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
        print("Visit this URL to authorize the app:", auth_url)
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

        status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        response = WebService.call(token_url, 'post', status_codes, headers=headers, data=data)
        
        if response.status_code == 200:
            response_body = response.json()
            self.spotify_access_token = response_body['access_token']
            # refresh_token = response_body.get('refresh_token')  # Store for later use
            print(self.spotify_access_token)
            return self.spotify_access_token
        else:
            print("Error:", response.json())
            return None
    
    ##############################
    #
    # generate ai playlist
    #
    ##############################
    def generate_ai_playlist(self, user_prompt, playlist_name, limit=10, public=False):
        headers = {
            'gpt_authorization': self.chatgpt_api_key,
            'spotify_authorization': self.spotify_access_token
        }
        data = {
            'user_prompt': user_prompt,
            'playlist_name': playlist_name,
            'limit': limit,
            'public': public
        }

        url = f'{self.api_endpoint}/generate-ai-playlist'
        response = WebService.call(url, 'post', [200], headers=headers, data=json.dumps(data))
        response_body = response.json()
        if response.status_code != 200:
            print(f'Status Code {response.status_code}: {response_body['message']}')
            return (None, None)

        tracks = []
        for track_data in response_body['data']['tracks']:
            id = track_data['id']
            name = track_data['name']
            artists = track_data['artists']
            album_cover_base64 = track_data['album_cover_base64']

            track = Track(id, name, artists, album_cover_base64)
            tracks.append(track)
        
        playlist_url = response_body['data']['playlist_url']

        return (tracks, playlist_url)

    ########################################
    #
    # generate personalized playlist
    #
    ########################################
    def generate_personalized_playlist(self, playlist_name, num_playlists=10, include_private=False, limit=10, public=False):
        headers = {
            'gpt_authorization': self.chatgpt_api_key,
            'spotify_authorization': self.spotify_access_token
        }
        data = {
            'playlist_name': playlist_name,
            'num_playlists': num_playlists,
            'include_private': include_private,
            'limit': limit,
            'public': public
        }

        url = f'{self.api_endpoint}/generate-personalized-playlist'
        response = WebService.call(url, 'post', [200], headers=headers, data=json.dumps(data))
        response_body = response.json()
        if response.status_code != 200:
            print(f'Status Code {response.status_code}: {response_body['message']}')
            return (None, None)
        print(response_body)

        tracks = []
        for track_data in response_body['data']['tracks']:
            id = track_data['id']
            name = track_data['name']
            artists = track_data['artists']
            album_cover_base64 = track_data['album_cover_base64']

            track = Track(id, name, artists, album_cover_base64)
            tracks.append(track)
        
        playlist_url = response_body['data']['playlist_url']

        return (tracks, playlist_url)
    
    ##############################
    #
    # generate image playlist
    #
    ##############################
    def upload_image(self, image_name):
        short_filename = os.path.basename(image_name)
        name, extension = os.path.splitext(short_filename)
        if extension.lower() not in ['.jpg', '.jpeg', '.png']:
            print('unsupported filetype')
        
        key_name = f'{name}-{uuid.uuid4()}{extension}'
        self.bucket.upload_file(image_name,
                                key_name,
                                ExtraArgs={
                                    'ACL': 'public-read',
                                    'ContentType': f'image/{extension[1:]}'
                                    })

        return key_name
    
    def generate_image_playlist(self, playlist_name, image_name, limit=10, public=False):
        key_name = self.upload_image(image_name)

        data = {
            'S3Bucket': self.bucket_name,
            'S3Object': key_name
        }
        url = f'{self.api_endpoint}/image-detect-labels'

        response = WebService.call(url, 'get', [200], data=json.dumps(data))
        response_body = response.json()
        if response.status_code != 200:
            print(f'Status Code {response.status_code}: {response_body['message']}')
            return (None, None)
        
        labels = response_body['data']
        print(labels)

        headers = {
            'gpt_authorization': self.chatgpt_api_key,
            'spotify_authorization': self.spotify_access_token
        }
        data = {
            'labels': labels,
            'playlist_name': playlist_name,
            'limit': limit,
            'public': public
        }
        url = f'{self.api_endpoint}/generate-image-playlist'
        response = WebService.call(url, 'post', [200], headers=headers, data=json.dumps(data))
        response_body = response.json()
        if response.status_code != 200:
            print(f'Status Code {response.status_code}: {response_body['message']}')
            return (None, None)

        tracks = []
        for track_data in response_body['data']['tracks']:
            id = track_data['id']
            name = track_data['name']
            artists = track_data['artists']
            album_cover_base64 = track_data['album_cover_base64']

            track = Track(id, name, artists, album_cover_base64)
            tracks.append(track)
        
        playlist_url = response_body['data']['playlist_url']

        return (tracks, playlist_url)
