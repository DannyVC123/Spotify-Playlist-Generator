import requests

import os

import base64
from io import BytesIO
from PIL import Image, ImageTk

class Track:
    folder = './album_covers'

    def __init__(self, id, name, artists, album_cover_base64):
        self.id = id
        self.name = name
        self.artists = artists

        self.album_cover = self.base64_to_image(album_cover_base64)
    
    
    def base64_to_image(self, base64_string):
        image_data = base64.b64decode(base64_string)
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        image = image.resize((110, 110))
        image_tk = ImageTk.PhotoImage(image)
        return image_tk
    
    def get_uri(self):
        return f'spotify:track:{self.id}'
    
    def __str__(self):
        str = f'{self.name}'
        for artist in self.artists:
            str = f'{str}\n  {artist}'
        return str