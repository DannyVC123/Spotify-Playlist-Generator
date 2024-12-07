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

# search
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

def create_slider(self, name, frame, min, max, increments, row, save_list):
    label = tk.Label(frame, text=f'{name}:', font=('Arial', 16, 'bold'))
    label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
    
    var = tk.DoubleVar()
    slider = tk.Scale(frame, variable=var, from_=min, to=max, resolution=increments, orient='horizontal', width=10)
    var.set((min + max) / 2)
    slider.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

    save_list.append(slider)

def refresh_access_token(refresh_token):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = WebService.call(url, 'post', headers=headers, data=data)
    response_body = response.json()
    if response.status_code not in [200, 201, 202, 204]:
        print(response_body)
        return None
    
    new_access_token = response_body['access_token']
    return new_access_token