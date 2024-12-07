import requests
import base64

class Track:
    def __init__(self, id, name, artists, album_cover_url):
        self.id = id
        self.name = name
        self.artists = artists

        self.album_cover_base64 = self.download_and_encode_album_cover(album_cover_url)
    
    def download_and_encode_album_cover(self, album_cover_url):
        img_data = requests.get(album_cover_url).content
        base64_image = base64.b64encode(img_data).decode('utf-8')
        return base64_image
    
    def get_uri(self):
        return f'spotify:track:{self.id}'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "artists": [artist.to_dict() for artist in self.artists],
            "album_cover_base64": self.album_cover_base64
        }
    
    def __str__(self):
        str = f'{self.name}'
        for artist in self.artists:
            str = f'{str}\n  {artist}'
        return str