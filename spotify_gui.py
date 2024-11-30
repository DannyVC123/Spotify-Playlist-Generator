import webbrowser
import json

from dotenv import load_dotenv
import os
import shutil

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from image_gallery import ImageGallery

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

        self.chatgpt_api_key = os.getenv('CHATGPT_API_KEY')

        self.create_ui()
        # self.display_tracks()
        self.root.mainloop()

        if os.path.exists(Track.folder):
            shutil.rmtree(Track.folder)
    
    ##############################
    #
    # create UI
    #
    ##############################
    def create_ui(self):
        # Window
        self.root = tk.Tk()
        self.root.title('Spotify Playlist Generator')
        self.root.geometry(f'{SpotifyGUI.width}x{SpotifyGUI.height}')

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        self.tabs = {}
        self.create_login_tab()
        self.create_manual_tab()
        self.create_ai_tab()
    
    def create_login_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Login to Spotify")
        self.tabs['login'] = tab

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
        self.tabs['manual'] = tab

        # Title
        title_label = tk.Label(tab, text='Manual Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Frame for number of songs and playlist name
        params_frame = tk.Frame(tab)
        params_frame.pack(pady=10)

        # Parameters
        self.manual_params = []

        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=params_frame, box_size=5, row=0, save_list=self.manual_params)
        
        param_names = ['Danceability', 'Energy', 'Valence (Mood)', 'Instrumentalness']
        for i in range(len(param_names)):
            self.create_slider(param_names[i], frame=params_frame, min=0, max=1, increments=0.1, row=i+1, save_list=self.manual_params)
        self.create_slider('Popularity', frame=params_frame, min=0, max=100, increments=1, row=5, save_list=self.manual_params)
        self.create_slider('Tempo', frame=params_frame, min=30, max=200, increments=1, row=6, save_list=self.manual_params)
        
        self.create_textbox('Playlist Name', frame=params_frame, box_size=15, row=7, save_list=self.manual_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_ai_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_ai_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="AI Playlist Generator")
        self.tabs['ai'] = tab

        # Title
        title_label = tk.Label(tab, text='AI Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Playlist Prompt
        playlist_prompt_label = tk.Label(tab, text='Playlist Prompt:', font=('Arial', 16, 'bold'))
        playlist_prompt_label.pack(pady=5)

        self.playlist_prompt_textbox = tk.Text(tab, width=50, height=8, font=('Arial', 16), wrap=tk.WORD)
        self.playlist_prompt_textbox.pack(pady=5)

        # Frame for number of songs and playlist name
        params_frame = tk.Frame(tab)
        params_frame.pack(pady=10)

        # Params
        self.ai_params = []
        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=params_frame, box_size=5, row=0, save_list=self.ai_params)
        self.create_textbox('Playlist Name', frame=params_frame, box_size=15, row=1, save_list=self.ai_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_ai_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_textbox(self, name, frame, box_size, row, save_list):
        label = tk.Label(frame, text=name, font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

        textbox = tk.Entry(frame, width=box_size)
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
    
    ##############################
    #
    # get token
    #
    ##############################
    def initialize_external_clients(self):
        callback_url = self.callback_url_textbox.get('1.0', 'end-1c')
        
        widgets = self.tabs['login'].winfo_children()
        if isinstance(widgets[-1], tk.Label):
            widgets[-1].destroy()

        response_label = tk.Label(self.tabs['login'], font=('Arial', 16, 'bold'), fg='green')
        response_label.pack(pady=10)
        
        if not callback_url:
            response_label.config(text='No URL enetered', fg='red')
            return
        
        access_token = self.client.get_token(callback_url)
        if not access_token:
            response_label.config(text='Login Error', fg='red')
            return
        response_label.config(text='Login Successful!', fg='green')

        self.spotify_client = SpotifyClient(access_token, self.user_id)
        self.chatpgt_client = ChatGPTClient(self.chatgpt_api_key)
    
    ##############################
    #
    # generate ai playlist
    #
    ##############################
    def generate_ai_playlist(self):
        user_prompt = self.playlist_prompt_textbox.get('1.0', 'end-1c')
        # params_json = self.gemini_client.get_recommendations_json(user_prompt)
        # print(params_json)

        params_json = '''[
    {
        "title": "Spring Day",
        "artist": "BTS",
        "album": "You Never Walk Alone"
    },
    {
        "title": "Stay With Me",
        "artist": "Chanyeol, Punch",
        "album": "Guardian: The Lonely and Great God (Original Soundtrack)"
    },
    {
        "title": "Only Then",
        "artist": "Roy Kim",
        "album": "Begin Again 2"
    },
    {
        "title": "Love Scenario",
        "artist": "iKON",
        "album": "Return"
    },
    {
        "title": "LOSER",
        "artist": "BIGBANG",
        "album": "MADE"
    },
    {
        "title": "Eyes, Nose, Lips",
        "artist": "Taeyang",
        "album": "RISE"
    },
    {
        "title": "12월의 기적 (Miracles In December)",
        "artist": "EXO",
        "album": "Miracles in December"
    },
    {
        "title": "Hug Me",
        "artist": "Jung Joon Young, Younha",
        "album": "JJY"
    },
    {
        "title": "Beautiful",
        "artist": "Crush",
        "album": "Guardian: The Lonely and Great God (Original Soundtrack)"
    },
    {
        "title": "Breath",
        "artist": "Lee Hi",
        "album": "Seoulite"
    }
]'''
        tracks = self.spotify_client.get_all_tracks(json.loads(params_json))
        
        if tracks:
            self.album_gallery = ImageGallery(self.tabs['ai'], tracks)
            playlist_name = self.ai_params[1].get()
            
            playlist = self.spotify_client.create_playlist(playlist_name)
            playlist_url = self.spotify_client.populate_playlist(playlist, tracks)
            webbrowser.open(playlist_url)

SpotifyGUI()