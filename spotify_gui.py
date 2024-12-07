import webbrowser
import json

from dotenv import load_dotenv
import os
import shutil

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from image_gallery import ImageGallery

from client import Client
from image_recognition import ImageRecognition

from track import Track

class SpotifyGUI:
    width, height = 800, 800

    def __init__(self):
        self.client = Client()

        self.create_ui()
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
        self.create_ai_tab()
        self.create_personalized_tab()
        self.create_image_tab()
    
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

        submit_url_button = tk.Button(tab, text='Submit URL', width=15, command=self.login)
        submit_url_button.pack(pady=5)
    
    def create_ai_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="AI Playlist Generator")
        self.tabs['ai'] = tab

        # Title
        title_label = tk.Label(tab, text='AI Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Playlist Prompt
        playlist_prompt_label = tk.Label(tab, text='Playlist Prompt', font=('Arial', 16, 'bold'))
        playlist_prompt_label.pack(pady=5)

        self.playlist_prompt_textbox = tk.Text(tab, width=50, height=8, font=('Arial', 16), wrap=tk.WORD)
        self.playlist_prompt_textbox.pack(pady=5)

        # Frame for number of songs and playlist name
        params_frame = tk.Frame(tab)
        params_frame.pack(pady=10)

        # Params
        self.ai_params = []
        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=params_frame, box_size=5, row=0, save_list=self.ai_params)
        self.create_checkbox('Public Playlist?', frame=params_frame, row=1, save_list=self.ai_params)
        self.create_textbox('Playlist Name', frame=params_frame, box_size=15, row=2, save_list=self.ai_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_ai_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_personalized_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Personalized Playlist Generator")
        self.tabs['personalized'] = tab

        # Title
        title_label = tk.Label(tab, text='Personalized Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Frame for number of songs and playlist name
        params_frame = tk.Frame(tab)
        params_frame.pack(pady=10)

        # Params
        self.personalized_params = []
        self.create_textbox('Number of Recent Playlists to Search', frame=params_frame, box_size=5, row=0, save_list=self.personalized_params)
        self.create_checkbox('Search Private Playlists?', frame=params_frame, row=1, save_list=self.personalized_params)
        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=params_frame, box_size=5, row=2, save_list=self.personalized_params)
        self.create_checkbox('Public Playlist?', frame=params_frame, row=3, save_list=self.personalized_params)
        self.create_textbox('Playlist Name', frame=params_frame, box_size=15, row=4, save_list=self.personalized_params)

        # Submit button
        submit_prompt_button = tk.Button(tab, text='Generate Playlist', width=15, command=self.generate_personalized_playlist)
        submit_prompt_button.pack(pady=5)
    
    def create_image_tab(self):
        # Tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Playlist Generator From Image")
        self.tabs['image'] = tab

        # Title
        title_label = tk.Label(tab, text='Playlist Generator From Image', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Select image button
        select_image = tk.Button(tab, text='Select Image From Computer', command=self.display_image)
        select_image.pack(pady=5)
        # Frame for number of songs and playlist name
        params_frame = tk.Frame(tab)
        params_frame.pack(pady=10)

        # Params
        self.image_params = []
        self.create_textbox('Number of Songs in Playlist (Default 10)', frame=params_frame, box_size=5, row=2, save_list=self.image_params)
        self.create_checkbox('Public Playlist?', frame=params_frame, row=3, save_list=self.image_params)
        self.create_textbox('Playlist Name', frame=params_frame, box_size=15, row=4, save_list=self.image_params)
    
    def create_textbox(self, name, frame, box_size, row, save_list):
        label = tk.Label(frame, text=name, font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

        textbox = tk.Entry(frame, width=box_size)
        textbox.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

        save_list.append(textbox)
    
    def create_checkbox(self, name, frame, row, save_list):
        label = tk.Label(frame, text=name, font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

        var = tk.BooleanVar()
        checkbutton = tk.Checkbutton(frame, variable=var, onvalue=True, offvalue=False)
        checkbutton.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
        checkbutton.var = var

        save_list.append(checkbutton)
    
    ##############################
    #
    # get token
    #
    ##############################
    def login(self):
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
    
    ##############################
    #
    # generate ai playlist
    #
    ##############################
    def generate_ai_playlist(self):
        user_prompt = self.playlist_prompt_textbox.get('1.0', 'end-1c')
        limit = self.ai_params[0].get()
        public = self.ai_params[1].var.get()
        try:
            limit = int(limit)
        except:
            limit = 10
        playlist_name = self.ai_params[2].get()

        tracks, playlist_url = self.client.generate_ai_playlist(user_prompt, playlist_name, limit, public)
        if not tracks or not playlist_url:
            return
        
        self.album_gallery = ImageGallery(self.tabs['ai'], tracks)
        open_playlist = tk.Button(self.tabs['ai'], text='Open Playlist', width=15, command=lambda: webbrowser.open(playlist_url))
        open_playlist.pack(pady=5)
    
    ########################################
    #
    # generate personalized playlist
    #
    ########################################
    def generate_personalized_playlist(self):
        num_playlists = self.personalized_params[0].get()
        try:
            num_playlists = int(num_playlists)
        except:
            num_playlists = 5
        include_private = self.personalized_params[1].var.get()
        limit = self.personalized_params[2].get()
        try:
            limit = int(limit)
        except:
            limit = 10
        public = self.personalized_params[3].var.get()
        playlist_name = self.personalized_params[4].get()

        tracks, playlist_url = self.client.generate_personalized_playlist(playlist_name, num_playlists, include_private, limit, public)
        if not tracks or not playlist_url:
            return
        
        self.album_gallery = ImageGallery(self.tabs['personalized'], tracks)
        open_playlist = tk.Button(self.tabs['personalized'], text='Open Playlist', width=15, command=lambda: webbrowser.open(playlist_url))
        open_playlist.pack(pady=5)
    
    ##############################
    #
    # generate image playlist
    #
    ##############################
    def display_image(self):
        f_types = [('JPG Files', '*.jpg'), ('JPEG Files', '*.jpeg'), ('PNG Files', '*.png')]
        self.filename = filedialog.askopenfilename(filetypes=f_types)
        
        if not self.filename:
            return
        
        img = Image.open(self.filename)

        width, height = img.size 
        new_height = 200
        new_width = int(new_height / height * width)
        img_resized = img.resize((new_width, new_height))
        img_tk = ImageTk.PhotoImage(img_resized)

        label = tk.Label(self.tabs['image'], image=img_tk)
        label.image = img_tk
        label.pack(pady=5)
        
        # Submit button
        submit_prompt_button = tk.Button(self.tabs['image'], text='Generate Playlist', width=15, command=self.generate_image_playlist)
        submit_prompt_button.pack(pady=5)

        image_recognition = ImageRecognition()
        key_name = image_recognition.upload_image(self.filename)
        image_recognition.detect_labels(key_name)
    
    def generate_image_playlist(self):
        limit = self.image_params[0].get()
        try:
            limit = int(limit)
        except:
            limit = 10
        public = self.image_params[1].var.get()
        playlist_name = self.image_params[2].get()

        tracks, playlist_url = self.client.generate_image_playlist(playlist_name, self.filename, limit, public)
        if not tracks or not playlist_url:
            return
        
        self.album_gallery = ImageGallery(self.tabs['image'], tracks)
        open_playlist = tk.Button(self.tabs['image'], text='Open Playlist', width=15, command=lambda: webbrowser.open(playlist_url))
        open_playlist.pack(pady=5)

SpotifyGUI()