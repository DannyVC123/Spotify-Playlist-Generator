import json
import logging
import traceback
import os

from chatgpt_client import ChatGPTClient
from spotify_client import SpotifyClient

def lambda_handler(event, context):
    try:
        if 'headers' not in event:
            return error_response("Invalid request: Missing headers")
        
        headers = event['headers']
        chatgpt_client, spotify_client = initialize_clients(headers)
        
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        
        required_fields = ['user_prompt', 'playlist_name']
        for field in required_fields:
            if field not in body:
                return error_response(f"Missing required field: {field}")
        
        user_prompt = body['user_prompt']
        playlist_name = body['playlist_name']
        limit = body.get('limit', 10)
        public = body.get('public', False)
        
        response = generate_playlist(chatgpt_client, spotify_client,
                                    user_prompt, playlist_name, limit, public)
        return response
    except Exception as e:
        # Catch any unexpected errors
        return error_response(f"Error generating playlist: {str(e)}")

def initialize_clients(headers):
    if 'gpt_authorization' not in headers:
        raise ValueError("Missing GPT authorization key")
    
    if 'spotify_authorization' not in headers:
        raise ValueError("Missing Spotify authorization key")
    
    chat_gpt_api_key = headers['gpt_authorization']
    spotify_api_key = headers['spotify_authorization']
    
    chatgpt_client = ChatGPTClient(chat_gpt_api_key)
    spotify_client = SpotifyClient(spotify_api_key)
    
    return (chatgpt_client, spotify_client)

def generate_playlist(chatgpt_client, spotify_client, user_prompt, playlist_name, limit=10, public=False):
    tracks_json = chatgpt_client.get_recommendations_json(user_prompt, limit)
    tracks = spotify_client.get_all_tracks(tracks_json, limit)
    if not tracks:
        return error_response('Get Tracks Failed.')
    
    playlist = spotify_client.create_playlist(playlist_name, public=public)
    if not playlist:
        return error_response('Create Playlist Failed.')
    
    playlist_url = spotify_client.populate_playlist(playlist, tracks)
    print('playlist_url', playlist_url)
    if not playlist_url:
        return error_response('Populate Playlist Failed.')
    
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Playlist generated successfully',
            'data': {
                'tracks': [track.to_dict() for track in tracks],
                'playlist_url': playlist_url
            }
        })
    }
    return response

def error_response(message):
    return {
        'statusCode': 500,
        'body': json.dumps({
            'message': message
        })
    }