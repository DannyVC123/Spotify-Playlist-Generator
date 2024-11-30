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
from tkinter import ttk
from PIL import Image, ImageTk

from web_service import WebService
from client import Client
from spotify_client import SpotifyClient
from chatgpt_client import ChatGPTClient

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

        self.gemini_api_key = os.getenv('CHATGPT_API_KEY')

        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        # Window
        self.root = tk.Tk()
        self.root.title('Spotify Playlist Generator')
        self.root.geometry(f'{SpotifyGUI.width}x{SpotifyGUI.height}')

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        self.create_login_tab()
        self.create_manual_tab()
        self.create_prompt_tab()
    
    def create_login_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Login to Spotify")

        # Title
        title_label = tk.Label(tab, text='Login to Spotify', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Frame for login section
        login_frame = tk.Frame(tab)
        login_frame.pack(pady=10)

        # Login Label and Button
        login_label = tk.Label(login_frame, text='Click Here to Login:', font=('Arial', 16, 'bold'))
        login_label.grid(row=0, column=0, padx=5, pady=5)

        login_button = tk.Button(login_frame, text='Login to Spotify', width=15, command=self.client.autorize)
        login_button.grid(row=0, column=1, padx=5, pady=5)

        # Authorization Code
        callback_url_label = tk.Label(tab, text='Paste Callback URL:', font=('Arial', 16, 'bold'))
        callback_url_label.pack(pady=5)

        self.callback_url_textbox = tk.Text(tab, width=80, height=4, font=('Arial', 16))
        self.callback_url_textbox.pack(pady=5)

        submit_url_button = tk.Button(tab, text='Submit URL', width=15, command=self.initialize_external_clients)
        submit_url_button.pack(pady=5)
    
    def create_manual_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manual Generator")

        # Title
        title_label = tk.Label(tab, text='Manual Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Frame for number of songs and playlist name
        songs_frame = tk.Frame(tab)
        songs_frame.pack(pady=10)

        # Parameters
        self.manual_params = []

        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=songs_frame, row=0, save_list=self.manual_params)
        
        param_names = ['Danceability', 'Energy', 'Valence (Mood)', 'Instrumentalness']
        for i in range(len(param_names)):
            self.create_slider(param_names[i], frame=songs_frame, min=0, max=1, increments=0.1, row=i+1, save_list=self.manual_params)
        self.create_slider('Popularity', frame=songs_frame, min=0, max=100, increments=1, row=5, save_list=self.manual_params)
        self.create_slider('Tempo', frame=songs_frame, min=30, max=200, increments=1, row=6, save_list=self.manual_params)
        
        self.create_textbox('Playlist Name', frame=songs_frame, row=7, save_list=self.manual_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_ai_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_prompt_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="AI Playlist Generator")

        # Title
        title_label = tk.Label(tab, text='AI Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Playlist Prompt
        playlist_prompt_label = tk.Label(tab, text='Playlist Prompt:', font=('Arial', 16, 'bold'))
        playlist_prompt_label.pack(pady=5)

        self.playlist_prompt_textbox = tk.Text(tab, width=50, height=8, font=('Arial', 16), wrap=tk.WORD)
        self.playlist_prompt_textbox.pack(pady=5)

        # Frame for number of songs and playlist name
        songs_frame = tk.Frame(tab)
        songs_frame.pack(pady=10)

        # Params
        self.ai_params = []
        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=songs_frame, row=0, save_list=self.ai_params)
        self.create_textbox('Playlist Name', frame=songs_frame, row=1, save_list=self.ai_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_ai_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_textbox(self, name, frame, row, save_list):
        label = tk.Label(frame, text=name, font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

        textbox = tk.Entry(frame, width=5)
        textbox.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

        save_list.append(textbox)

    def create_slider(self, name, frame, min, max, increments, row, save_list):
        label = tk.Label(frame, text=f'{name}:', font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        
        var = tk.DoubleVar()
        slider = tk.Scale(frame, variable=var, from_=min, to=max, resolution=increments, orient='horizontal', width=10)
        var.set((min + max) / 2)
        slider.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

        save_list.append(slider)
    
    def initialize_external_clients(self):
        # Spotify
        callback_url = self.callback_url_textbox.get('1.0', 'end-1c')
        print(callback_url)
        if not callback_url:
            return
        access_token = self.client.get_token(callback_url)
        print(access_token)

        self.spotify_client = SpotifyClient(access_token, self.user_id)

        # Gemini
        self.gemini_client = ChatGPTClient(self.gemini_api_key)
    
    def generate_ai_playlist(self):
        user_prompt = self.playlist_prompt_textbox.get('1.0', 'end-1c')
        params_json = self.gemini_client.get_recommendations_json(user_prompt)
        print(params_json)
        tracks = self.spotify_client.get_all_tracks(params_json)
        
        if tracks:
            self.display_tracks(tracks)
            playlist_name = self.ai_params[1].get()
            playlist = self.spotify_client.create_playlist(playlist_name)
            playlist_url = self.spotify_client.populate_playlist(playlist, tracks)
            webbrowser.open(playlist_url)
    
    def display_tracks(self, recommended_tracks):
        songs_frame = tk.Frame(self.root)
        songs_frame.pack(pady=10)
        
        for i, track in enumerate(recommended_tracks[0:5]):
            img_name = track.download_album_cover()

            img = Image.open(img_name)
            img = img.resize((120, 120))
            tk_img = ImageTk.PhotoImage(img)

            img_label = tk.Label(songs_frame, image=tk_img)
            img_label.image = tk_img
            img_label.grid(row=0, column=i, padx=5)

            name_label = tk.Label(songs_frame, text=track.name, wraplength=120)
            name_label.grid(row=1, column=i, padx=5)

SpotifyGUI()