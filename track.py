import requests

import os

from PIL import Image, ImageTk

class Track:
    folder = './album_covers'

    def __init__(self, id, name, artists, album_cover_url):
        self.id = id
        self.name = name
        self.artists = artists

        self.album_cover = self.download_album_cover(album_cover_url)
    
    def download_album_cover(self, album_cover_url):
        img_data = requests.get(album_cover_url).content
        img_name = f'{Track.folder}/album_{self.id}.jpg'

        os.makedirs(Track.folder, exist_ok=True)
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        
        img = Image.open(img_name)
        img = img.resize((110, 110))
        album_cover = ImageTk.PhotoImage(img)

        return album_cover
    
    def get_uri(self):
        return f'spotify:track:{self.id}'
    
    def __str__(self):
        str = f'{self.name}'
        for artist in self.artists:
            str = f'{str}\n  {artist}'
        return str