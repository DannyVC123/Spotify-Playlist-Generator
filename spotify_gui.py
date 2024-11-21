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
import tkinter as tk

from web_service import WebService
from client import Client
from spotify_client import SpotifyClient
from track import Track
from playlist import Playlist

class SpotifyGUI:
    width, height = 800, 800

    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.user_id = os.getenv('USER_ID')
        self.client = Client(self.client_id, self.client_secret, self.redirect_uri)

        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        # Window
        self.root = tk.Tk()
        self.root.title('Spotify Playlist Generator')
        self.root.geometry(f'{SpotifyGUI.width}x{SpotifyGUI.height}')
        
        # Title
        title_label = tk.Label(self.root, text='Spotify Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Spacer
        spacer = tk.Label(self.root)
        spacer.pack(pady=5)

        # Frame for login section
        login_frame = tk.Frame(self.root)
        login_frame.pack(pady=10)

        # Login Label and Button
        login_label = tk.Label(login_frame, text='Click Here to Login:', font=('Arial', 16, 'bold'))
        login_label.grid(row=0, column=0, padx=5, pady=5)
        
        login_button = tk.Button(login_frame, text='Login to Spotify', width=15, command=self.client.autorize)
        login_button.grid(row=0, column=1, padx=5, pady=5)

        # Autorization Code
        callback_url_label = tk.Label(self.root, text='Paste Callback URL:', font=('Arial', 16, 'bold'))
        callback_url_label.pack(pady=5)

        self.callback_url_textbox = tk.Text(self.root, width=80, height=2, font=('Arial', 16))
        self.callback_url_textbox.pack(pady=5)

        submit_url_button = tk.Button(self.root, text='Submit URL', width=15, command=self.initialize_spotify_client)
        submit_url_button.pack(pady=5)

        # Spacer
        spacer2 = tk.Label(self.root)
        spacer2.pack(pady=5)

        # Playlist Prompt
        playlist_prompt_label = tk.Label(self.root, text='Paste Playlist JSON from ChatGPT:', font=('Arial', 16, 'bold'))
        playlist_prompt_label.pack(pady=5)

        self.playlist_prompt_textbox = tk.Text(self.root, width=50, height=8, font=('Arial', 16), wrap=tk.WORD)
        self.playlist_prompt_textbox.pack(pady=5)

        # Frame for number of songs and playlist name
        songs_frame = tk.Frame(self.root)
        songs_frame.pack(pady=10)

        # Num Songs Label and Textbox
        num_songs_label = tk.Label(songs_frame, text='Number of Songs in Playlist (Default 10):', font=('Arial', 16, 'bold'))
        num_songs_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.num_songs_textbox = tk.Entry(songs_frame, width=5)
        self.num_songs_textbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Playlist Name
        playlist_name_label = tk.Label(songs_frame, text='Playlist Name (ChatGPT will generate a name if empty):', font=('Arial', 16, 'bold'))
        playlist_name_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.playlist_name_textbox = tk.Entry(songs_frame, width=15)
        self.playlist_name_textbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Submit button
        submit_prompt_button = tk.Button(self.root, text='Generate Playlist', width=15, command=self.generate_playlist)
        submit_prompt_button.pack(pady=5)
    
    def initialize_spotify_client(self):
        callback_url = self.callback_url_textbox.get('1.0', 'end-1c')
        if not callback_url:
            return
        access_token = self.client.get_token(callback_url)
        print(access_token)

        self.spotify_client = SpotifyClient(access_token, self.user_id)
    
    def generate_playlist(self):
        params_json = self.playlist_prompt_textbox.get('1.0', 'end-1c')
        recommended_tracks = self.spotify_client.get_track_recommendations(params_json)
        if recommended_tracks:
            playlist_name = self.playlist_name_textbox.get()
            playlist = self.spotify_client.create_playlist(playlist_name)
            playlist_url = self.spotify_client.populate_playlist(playlist, recommended_tracks)
            webbrowser.open(playlist_url)


SpotifyGUI()