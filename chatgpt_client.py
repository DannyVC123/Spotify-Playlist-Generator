import openai

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

class ChatGPTClient:
    system_prompt = '''Interpret casual descriptions of music preferences and convert them into Spotify playlist JSON. Map descriptions to Spotify API parameters. The user will provide a general description of what they want in a playlist, without directly referencing Spotify API parameters.

IMPORTANT: Include ALL parameters that can be reasonably inferred from the user's description. Don't limit yourself to just the required parameters.

Required parameters:
- limit: Max tracks (default 10)
- seed_artists (list of strings): Mentioned artists
- seed_genres (list of strings): Mentioned genres
- target_danceability (0 to 1): Danceability (e.g., "upbeat" = 0.8, "chill" = 0.2)
- target_energy (0 to 1): Energy (e.g., "high energy" = 0.8, "relaxed" = 0.2)
- target_instrumentalness (0 to 1): Instrumentalness (e.g., "instrumental" = 0.8, "vocal" = 0.2)
- target_popularity (0 to 100): Popularity (e.g., "popular" = 80, "indie" = 30)
- target_tempo (BPM): Tempo (e.g., "fast" = 140, "moderate" = 100, "slow" = 70)
- target_valence (0 to 1): Mood (e.g., "happy" = 0.8, "sad" = 0.2)

Valid genres: [{genres}]

Parameter Mapping Rules:
1. Genre Mapping:
   - Direct mentions: "pop" → ["pop"], "rock" → ["rock"]
   - Implied genres: "electronic beats" → ["electronic", "dance"]
   - Multiple genres: "pop rock" → ["pop", "rock"]

2. Artist Mapping:
   - Direct mention of artists: "Taylor Swift" → ["Taylor Swift"]
   - Implied artists: "songs with a similar vibe to Ed Sheeran" → ["Ed Sheeran"]`
   - No artists mentioned: []

3. Mood/Energy Mapping:
   - "upbeat"/"energetic" → target_energy: 0.8, target_danceability: 0.8
   - "chill"/"relaxed" → target_energy: 0.2, target_danceability: 0.2
   - "happy" → target_valence: 0.8
   - "sad" → target_valence: 0.2

4. Tempo Mapping:
   - "fast"/"uptempo" → target_tempo: 140
   - "moderate" → target_tempo: 100
   - "slow" → target_tempo: 70

5. Style Mapping:
   - "instrumental" → target_instrumentalness: 0.8
   - "vocal" → target_instrumentalness: 0.2
   - "loud" → target_loudness: 0.8
   - "soft" → target_loudness: 0.2

6. Popularity Mapping:
   - "popular"/"mainstream" → target_popularity: 80
   - "indie"/"underground" → target_popularity: 30

Example 1:
Input: "I want upbeat pop songs by Taylor Swift and Ed Sheeran"
Output:
{{
    "limit": 10,
    "seed_artists": ["Taylor Swift", "Ed Sheeran"],
    "seed_genres": ["pop"],
    "target_danceability": 0.8,
    "target_energy": 0.8,
    "target_instrumentalness": 0.2,
    "target_popularity": 80,
    "target_tempo": 120,
    "target_valence": 0.8
}}

Example 2:
Input: "Give me some chill instrumental jazz for studying"
Output:
{{
    "limit": 10,
    "seed_artists": [],
    "seed_genres": ["jazz"],
    "target_danceability": 0.2,
    "target_energy": 0.2,
    "target_instrumentalness": 0.8,
    "target_popularity": 30,
    "target_tempo": 70,
    "target_valence": 0.2
}}

Based on the user's description, generate a JSON object that includes ALL applicable parameters. Include optional parameters whenever you can reasonably infer them from the description. Output only the JSON object with no additional text.'''

    def __init__(self, api_key):
        openai.api_key = api_key
        self.model = 'gpt-4o-mini'
    
    def get_recommendations_json(self, user_prompt, limit=10):
        base_prompt = '''You are an assistant that only responds in JSON. Create a list of {limit} unique songs based off the following statement: "{user_prompt}". Include "title", "artist", "album". An example response is:"
[
    {{
        "title": "Hey Jude",
        "artist": "The Beatles",
        "album": "The Beatles (White Album)"
    }}
]"'''
        full_prompt = base_prompt.format(limit=limit + 5, user_prompt=user_prompt)
        messages = [
            {
                'role': 'user',
                'content': full_prompt
            }
        ]

        response = openai.chat.completions.create(model=self.model, temperature=0.1, max_tokens=3000, messages=messages)
        content = response.choices[0].message.content
        print(content)

        tracks_json = json.loads(content[content.find("[") : content.rfind("]") + 1])
        print(tracks_json)
        return tracks_json

