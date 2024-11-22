import requests

import os

class Track:
    def __init__(self, id, name, artists, album_cover_url):
        self.id = id
        self.name = name
        self.artists = artists
        self.album_cover_url = album_cover_url
    
    def get_uri(self):
        return f'spotify:track:{self.id}'
    
    def download_album_cover(self):
        img_data = requests.get(self.album_cover_url).content
        img_name = f'./album_covers/album_{self.id}.jpg'

        os.makedirs('./album_covers', exist_ok=True)
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        
        return img_name
    
    def __str__(self):
        str = f'{self.name}'
        for artist in self.artists:
            str = f'{str}\n  {artist}\n  {self.album_cover_url}'
        return str