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