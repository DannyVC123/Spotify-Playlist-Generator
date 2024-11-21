import json
import requests
import webbrowser

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from web_service import WebService
from spotify_client import SpotifyClient

system_prompt = '''Interpret casual descriptions of music preferences and convert them into Spotify playlist JSON. Map descriptions to Spotify API parameters.

Required parameters:
limit: Max tracks (default 10).

Optional parameters:
seed_artists (list of strings): Mentioned artists
seed_genres (list of strings): Mentioned genres (e.g., "pop", "rock", "disney")
target_danceability (0 to 1): Danceability (e.g., "upbeat" = 1, "chill" = 0)
target_energy (0 to 1): Energy (e.g., "high energy" = 1, "relaxed" = 0)
target_instrumentalness (0 to 1): Instrumentalness (e.g., "instrumental" = 1, "vocal" = 0)
target_loudness (0-1): Loudness (e.g., "loud" = 1, "soft" = 0)
target_popularity (0 to 100): Popularity score (e.g., "popular" = 100, "less known" = 0)
target_tempo (BPM): Tempo (e.g., "fast" = high, "slow" = low)
target_valence (0 to 1): Mood (e.g., "happy" = high, "sad" = low)

Genre list:
{}

Please output the JSON and nothing else.'''

class ChatGPTClient:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
    
    def get_recommendations_json(genres, user_prompt):
        sys_prompt_w_genres = system_prompt.format(', '.join(genres))

